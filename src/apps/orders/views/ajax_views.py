import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.views import View

from apps.clients.models import Client
from apps.orders.models import Order, OrderItem
from apps.products.models import Product


class SearchClientsView(LoginRequiredMixin, View):
    """
    Handles a request to search for clients based on their phone numbers.

    This view requires the user to be authenticated. It restricts the request method
    to GET only and retrieves clients whose phone numbers match the search query.
    The client data is sorted by their orders count in descending order and limited
    to a maximum of 10 results. If the search query (phone) is less than 3 characters,
    it directly returns an empty client list.
    """

    def get(self, request):
        """
        :param request: HttpRequest object that includes any search parameters,
            specifically the phone number.
        :type request: HttpRequest
        :return: A JsonResponse object containing a list of matched clients with their
            details and the total count of matched entries.
        :rtype: JsonResponse
        """
        phone = request.GET.get("phone", "").strip()

        if len(phone) < 3:
            return JsonResponse({"clients": []})

        clients = Client.objects.filter(
            Q(phone__icontains=phone) | Q(phone__startswith=phone)
        ).order_by("-orders_count")[:10]

        clients_data = [
            {
                "id": client.id,
                "first_name": client.first_name,
                "last_name": client.last_name,
                "phone": client.phone,
                "email": client.email,
                "full_name": client.full_name,
                "orders_count": client.orders_count,
                "total_spent": str(client.total_spent)
            }
            for client in clients
        ]

        return JsonResponse({
            "clients": clients_data,
            "count": len(clients_data)
        })


class SearchProductsView(LoginRequiredMixin, View):
    """
    Search for products based on a query string and return relevant results as JSON.

    This class allows users to search for products by name or category. It retrieves
    up to 20 matched products, along with their associated details such as name,
    price, category, stock, and optional emoji representation. The query must be
    at least two characters long.
    """

    def get(self, request):
        """
        :param request: The HTTP request object that contains the GET parameters, including
            the `q` query string for the search term.
        :type request: HttpRequest
        :return: A JsonResponse containing a list of matched products and the count of
            matches. The list of products includes details such as product ID, name,
            emoji, price, category, and stock.
        :rtype: JsonResponse
        """
        query = request.GET.get("q", "").strip()

        if len(query) < 2:
            return JsonResponse({"products": []})

        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query)
        ).select_related("category")[:20]

        products_data = [
            {
                "id": product.id,
                "name": product.name,
                "emoji": getattr(product, "emoji", "🌹"),
                "price": str(product.price),
                "category": product.category.name if product.category else "Без категорії",
                "stock": product.stock
            }
            for product in products
        ]

        return JsonResponse({
            "products": products_data,
            "count": len(products_data)
        })


class CreateOrderAjaxView(LoginRequiredMixin, View):
    """
    Handles creating a new order via an AJAX POST request. This class validates
    the input JSON, processes the client and item data, and creates an order in
    the system. It ensures all required fields are provided and validates data
    accordingly. If the order creation is successful, it returns a serialized
    response with the order details.
    """

    @transaction.atomic
    def post(self, request):
        """
        :param request: Django HTTP request object containing the AJAX POST data.
        :type request: HttpRequest

        :raises ValidationError: If the order or order item data fails validation.
        :raises Client.DoesNotExist: If a client with a given ID does not exist.
        :raises Product.DoesNotExist: If a product with a specified ID does not exist.
        :raises KeyError: If required keys for products or items are missing.
        :raises json.JSONDecodeError: If the JSON data in the request body is malformed.
        :raises Exception: For any other general exceptions during processing.

        :return: JsonResponse with the success status, errors (if any), and the created
            order data on success. Includes HTTP status codes indicating the operation
            result.
        :rtype: JsonResponse
        """
        try:
            data = json.loads(request.body)

            if not data.get("items"):
                return JsonResponse({
                    "success": False,
                    "errors": {"items": "Додайте хоча б один товар"}
                }, status=400)

            needs_delivery = data.get("needs_delivery", False)

            if needs_delivery:
                if not data.get("delivery_address"):
                    return JsonResponse({
                        "success": False,
                        "errors": {
                            "delivery_address": "Адреса доставки обов'язкова, якщо потрібна доставка"}
                    }, status=400)

                if not data.get("delivery_date"):
                    return JsonResponse({
                        "success": False,
                        "errors": {
                            "delivery_date": "Дата доставки обов'язкова, якщо потрібна доставка"}
                    }, status=400)

            client = self._get_or_create_client(data)
            if isinstance(client, JsonResponse):
                return client

            order = Order(
                client=client,
                needs_delivery=needs_delivery,
                notes=data.get("notes", "")
            )

            if needs_delivery:
                order.delivery_address = data.get("delivery_address")
                order.delivery_date = data.get("delivery_date")
                order.delivery_time = data.get("delivery_time") or None

            try:
                order.clean()
            except ValidationError as e:
                return JsonResponse({
                    "success": False,
                    "errors": e.message_dict
                }, status=400)

            order.save()

            result = self._add_order_items(order, data.get("items", []))
            if isinstance(result, JsonResponse):
                return result

            order.update_total()

            order_data = serialize_order(order)

            return JsonResponse({
                "success": True,
                "order": order_data,
                "message": f"Замовлення #{order.id} успішно створено"
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": "Невірний формат JSON"
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)

    def _get_or_create_client(self, data):
        """
        Get or create a client based on the provided data.

        :param data: Dictionary containing client information
        :return: Client instance or JsonResponse with error
        """
        client_id = data.get("client_id")
        if client_id:
            try:
                return Client.objects.get(id=client_id)
            except Client.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "errors": {"client": "Клієнт не знайдений"}
                }, status=404)
        else:
            phone = data.get("client_phone")
            first_name = data.get("client_first_name")

            if not phone or not first_name:
                return JsonResponse({
                    "success": False,
                    "errors": {"client": "Вкажіть телефон та ім'я клієнта"}
                }, status=400)

            client, created = Client.objects.get_or_create(
                phone=phone,
                defaults={
                    "first_name": first_name,
                    "last_name": data.get("client_last_name", "")
                }
            )
            return client

    def _add_order_items(self, order, items_data):
        """
        Add items to the order.

        :param order: Order instance
        :param items_data: List of item dictionaries
        :return: None if successful, JsonResponse if error
        """
        for item_data in items_data:
            try:
                product = Product.objects.get(id=item_data["product_id"])

                order_item = OrderItem(
                    order=order,
                    product=product,
                    quantity=item_data["quantity"],
                    unit_price=product.price
                )

                try:
                    order_item.clean()
                except ValidationError as e:
                    order.delete()
                    return JsonResponse({
                        "success": False,
                        "errors": {"product": str(e)}
                    }, status=400)

                order_item.save()

            except Product.DoesNotExist:
                order.delete()
                return JsonResponse({
                    "success": False,
                    "errors": {"product": f"Товар з ID {item_data['product_id']} не знайдено"}
                }, status=404)
            except KeyError:
                order.delete()
                return JsonResponse({
                    "success": False,
                    "errors": {"items": "Невірний формат товарів"}
                }, status=400)

        return None


class UpdateOrderAjaxView(LoginRequiredMixin, View):
    """
    Updates the details of an order via a POST AJAX request. This class handles the process of
    updating an existing order with client information, items, delivery details, and other
    order-related data. If any data validation fails or required fields are missing, appropriate
    error messages are returned in the response.

    This class ensures transactional integrity during updates and provides an atomic operation
    for updating orders and their related entities. In case of errors or exceptions, the database
    state will not be partially updated.
    """

    @transaction.atomic
    def post(self, request, order_id):
        """
        :param request:
            The HTTP request object representing the client request. It should contain
            necessary order update data in its body in JSON format.
        :param order_id:
            An integer representing the unique ID of the order to be updated.

        :return:
            A JsonResponse containing the result of the update operation. If successful, the
            response includes the updated order's data and a success status. Upon failure,
            the response contains errors or an appropriate error message and HTTP status code.
        """
        try:
            order = Order.objects.select_related("client").prefetch_related("items").get(id=order_id)
            data = json.loads(request.body)

            if not data.get("items"):
                return JsonResponse({
                    "success": False,
                    "errors": {"items": "Додайте хоча б один товар"}
                }, status=400)

            needs_delivery = data.get("needs_delivery", False)

            if needs_delivery:
                if not data.get("delivery_address"):
                    return JsonResponse({
                        "success": False,
                        "errors": {
                            "delivery_address": "Адреса доставки обов'язкова, якщо потрібна доставка"}
                    }, status=400)

                if not data.get("delivery_date"):
                    return JsonResponse({
                        "success": False,
                        "errors": {
                            "delivery_date": "Дата доставки обов'язкова, якщо потрібна доставка"}
                    }, status=400)

            client = self._update_or_create_client(data)
            if isinstance(client, JsonResponse):
                return client

            order.client = client
            order.needs_delivery = needs_delivery
            order.notes = data.get("notes", "")

            if needs_delivery:
                order.delivery_address = data.get("delivery_address")
                order.delivery_date = data.get("delivery_date")
                order.delivery_time = data.get("delivery_time") or None
            else:
                order.delivery_address = None
                order.delivery_date = None
                order.delivery_time = None

            try:
                order.clean()
            except ValidationError as e:
                return JsonResponse({
                    "success": False,
                    "errors": e.message_dict
                }, status=400)

            order.save()

            result = self._update_order_items(order, data.get("items", []))
            if isinstance(result, JsonResponse):
                return result

            order.update_total()

            order_data = serialize_order(order)

            return JsonResponse({
                "success": True,
                "order": order_data,
                "message": f"Замовлення #{order.id} успішно оновлено"
            })

        except Order.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Замовлення не знайдено"
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": "Невірний формат JSON"
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)

    def _update_or_create_client(self, data):
        """
        Update existing client or create a new one.

        :param data: Dictionary containing client information
        :return: Client instance or JsonResponse with error
        """
        client_id = data.get("client_id")
        if client_id:
            try:
                client = Client.objects.get(id=client_id)
                updated = False
                if data.get("client_first_name") and client.first_name != data["client_first_name"]:
                    client.first_name = data["client_first_name"]
                    updated = True
                if data.get("client_last_name") and client.last_name != data["client_last_name"]:
                    client.last_name = data["client_last_name"]
                    updated = True
                if updated:
                    client.save()
                return client
            except Client.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "errors": {"client": "Клієнт не знайдений"}
                }, status=404)
        else:
            phone = data.get("client_phone")
            first_name = data.get("client_first_name")

            if not phone or not first_name:
                return JsonResponse({
                    "success": False,
                    "errors": {"client": "Вкажіть телефон та ім'я клієнта"}
                }, status=400)

            client, created = Client.objects.get_or_create(
                phone=phone,
                defaults={
                    "first_name": first_name,
                    "last_name": data.get("client_last_name", "")
                }
            )
            return client

    def _update_order_items(self, order, items_data):
        """
        Update order items - delete removed, update existing, create new.

        :param order: Order instance
        :param items_data: List of item dictionaries
        :return: None if successful, JsonResponse if error
        """
        items_to_keep = {}
        for item_data in items_data:
            item_id = item_data.get("id")
            if item_id:
                items_to_keep[item_id] = item_data

        existing_items = {item.id: item for item in order.items.all()}
        for item_id, item in existing_items.items():
            if item_id not in items_to_keep:
                item.delete()

        for item_data in items_data:
            item_id = item_data.get("id")
            product_id = item_data.get("product_id")
            quantity = item_data.get("quantity", 1)

            try:
                product = Product.objects.get(id=product_id)

                if item_id and item_id in existing_items:
                    item = existing_items[item_id]
                    item.product = product
                    item.quantity = quantity
                    item.unit_price = product.price

                    try:
                        item.clean()
                    except ValidationError as e:
                        return JsonResponse({
                            "success": False,
                            "errors": {"product": str(e)}
                        }, status=400)

                    item.save()
                else:
                    new_item = OrderItem(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=product.price
                    )

                    try:
                        new_item.clean()
                    except ValidationError as e:
                        return JsonResponse({
                            "success": False,
                            "errors": {"product": str(e)}
                        }, status=400)

                    new_item.save()

            except Product.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "errors": {"product": f"Товар з ID {product_id} не знайдено"}
                }, status=404)
            except KeyError:
                return JsonResponse({
                    "success": False,
                    "errors": {"items": "Невірний формат товарів"}
                }, status=400)

        return None


class UpdateOrderStatusView(LoginRequiredMixin, View):
    """
    Updates the status of an existing order and persists any associated notes. This
    class ensures that only valid status transitions occur and handles any
    errors encountered during the process. It provides appropriate responses
    depending on the success or failure of the operation.
    """

    def post(self, request, order_id):
        """
        :param request: The HTTP request object that contains metadata about the request
            and possible JSON data relevant to the order status update.
        :type request: HttpRequest
        :param order_id: An integer specifying the unique identifier of the order
            whose status is to be updated.
        :type order_id: int
        :return: JsonResponse containing success status, updated order data (if applicable),
            and any error or success messages.
        :rtype: JsonResponse
        """
        try:
            order = Order.objects.get(id=order_id)
            data = json.loads(request.body)
            new_status = data.get("status")
            notes = data.get("notes", "")

            if not new_status:
                return JsonResponse({
                    "success": False,
                    "error": "Не вказано новий статус"
                }, status=400)

            try:
                order.transition_to(
                    new_status,
                    user=request.user,
                    notes=notes
                )

                order_data = serialize_order(order)

                return JsonResponse({
                    "success": True,
                    "order": order_data,
                    "message": f"Статус змінено на \"{order.get_status_display()}\""
                })

            except ValidationError as e:
                return JsonResponse({
                    "success": False,
                    "error": str(e)
                }, status=400)

        except Order.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Замовлення не знайдено"
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": "Невірний формат JSON"
            }, status=400)


class AddOrderItemView(LoginRequiredMixin, View):
    """
    Adds an item to an existing order.

    This class allows a user to add a product as an item to an order. It verifies
    the existence of the order and product, handles quantity updates for existing
    items, and creates new items if they do not already exist in the order. The
    function adjusts the order's total cost accordingly after updating or adding
    items. If any validation errors occur, the function returns an appropriate
    JSON response with an error message.
    """

    @transaction.atomic
    def post(self, request, order_id):
        """
        :param request: HTTP request object, containing user and payload data
            (e.g., product_id, quantity) in its body.
        :type request: HttpRequest
        :param order_id: Identifier for the targeted order to which the product
            should be added.
        :type order_id: int
        :return: JSON response containing the success status, updated order details,
            or error message. If successful, it includes the updated order's details
            and a confirmation message. In cases of failure, it returns the error
            type and description.
        :rtype: JsonResponse
        """
        try:
            order = Order.objects.get(id=order_id)
            data = json.loads(request.body)

            product_id = data.get("product_id")
            quantity = data.get("quantity", 1)

            if not product_id:
                return JsonResponse({
                    "success": False,
                    "error": "Не вказано продукт"
                }, status=400)

            product = Product.objects.get(id=product_id)

            existing_item = order.items.filter(product=product).first()

            if existing_item:
                existing_item.quantity += quantity
                try:
                    existing_item.clean()
                except ValidationError as e:
                    return JsonResponse({
                        "success": False,
                        "error": str(e)
                    }, status=400)
                existing_item.save()
            else:
                new_item = OrderItem(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price
                )
                try:
                    new_item.clean()
                except ValidationError as e:
                    return JsonResponse({
                        "success": False,
                        "error": str(e)
                    }, status=400)
                new_item.save()

            order.update_total()

            order_data = serialize_order(order)

            return JsonResponse({
                "success": True,
                "order": order_data,
                "message": f"Товар \"{product.name}\" додано до замовлення"
            })

        except Order.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Замовлення не знайдено"
            }, status=404)
        except Product.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Продукт не знайдено"
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": "Невірний формат JSON"
            }, status=400)


class UpdateOrderItemView(LoginRequiredMixin, View):
    """
    Updates the quantity of a specific item in an order. This class retrieves the item
    associated with the given `order_id` and `item_id`, modifies its quantity as provided
    in the request body, validates the input, and saves the changes. Subsequently, it
    updates the total cost of the associated order and returns the updated order data.
    """

    @transaction.atomic
    def post(self, request, order_id, item_id):
        """
        :param request: The HTTP request object containing the JSON-formatted data with the
            updated quantity of the item.
        :type request: HttpRequest
        :param order_id: ID of the order to which the item belongs.
        :type order_id: int
        :param item_id: ID of the order item to be updated.
        :type item_id: int
        :return: A JsonResponse containing the success status, the updated order data (if
            successful), or an error message (if unsuccessful).
        :rtype: JsonResponse
        """
        try:
            item = OrderItem.objects.select_related("order").get(
                id=item_id,
                order_id=order_id
            )
            data = json.loads(request.body)

            quantity = data.get("quantity")

            if quantity is None or quantity < 1:
                return JsonResponse({
                    "success": False,
                    "error": "Невірна кількість"
                }, status=400)

            item.quantity = quantity

            try:
                item.clean()
            except ValidationError as e:
                return JsonResponse({
                    "success": False,
                    "error": str(e)
                }, status=400)

            item.save()

            item.order.update_total()

            order_data = serialize_order(item.order)

            return JsonResponse({
                "success": True,
                "order": order_data,
                "message": "Кількість оновлено"
            })

        except OrderItem.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Товар не знайдено"
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": "Невірний формат JSON"
            }, status=400)


class DeleteOrderItemView(LoginRequiredMixin, View):
    """
    Deletes an order item specified by order ID and item ID. If the item is the
    last one within its order, the deletion is disallowed, and an appropriate
    response is returned. Upon successful deletion of the item, the total of the
    order is updated, and the updated order details are serialized and returned.
    """

    def post(self, request, order_id, item_id):
        """
        :param request: HttpRequest object representing the incoming request.
        :param order_id: ID of the order the item belongs to.
        :type order_id: int
        :param item_id: ID of the item to be deleted.
        :type item_id: int
        :return: JsonResponse object indicating the success or failure of the operation
                 along with the updated order data if applicable.
        :rtype: JsonResponse
        """
        return self._delete_item(request, order_id, item_id)

    def delete(self, request, order_id, item_id):
        """
        Handle DELETE method (same logic as POST).
        """
        return self._delete_item(request, order_id, item_id)

    def _delete_item(self, request, order_id, item_id):
        """
        Internal method to handle item deletion logic.
        """
        try:
            item = OrderItem.objects.select_related("order").get(
                id=item_id,
                order_id=order_id
            )

            if item.order.items.count() <= 1:
                return JsonResponse({
                    "success": False,
                    "error": "Неможливо видалити останній товар. Видаліть замовлення повністю."
                }, status=400)

            order = item.order
            item.delete()

            order.update_total()

            order_data = serialize_order(order)

            return JsonResponse({
                "success": True,
                "order": order_data,
                "message": "Товар видалено"
            })

        except OrderItem.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Товар не знайдено"
            }, status=404)


class OrderDetailView(LoginRequiredMixin, View):
    """
    Fetches and returns order details based on the provided order ID. The method retrieves
    the order with related client and prefetched product items, serializes the order,
    and returns the relevant data in a JSON response.
    """

    def get(self, request, order_id):
        """
        :param request: The HTTP request object
        :type request: HttpRequest
        :param order_id: The ID of the order to retrieve
        :type order_id: int
        :return: A JSON response containing success status and order details if found,
            or an error message with a 404 status if the order does not exist
        :rtype: JsonResponse
        """
        try:
            order = Order.objects.select_related("client").prefetch_related(
                "items__product"
            ).get(id=order_id)

            order_data = serialize_order(order)

            return JsonResponse({
                "success": True,
                "order": order_data
            })

        except Order.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Замовлення не знайдено"
            }, status=404)


class CalculateOrderPriceView(LoginRequiredMixin, View):
    """
    Calculates the total price for a list of items provided as JSON data in the GET
    request. Each item in the list should contain the `product_id` identifying the
    product and `quantity` indicating the number of units to be ordered. This view
    returns a JSON response with detailed item prices, subtotals, and the total
    order price.
    """

    def get(self, request):
        """
        :param request: The HTTP request object with GET data containing the `items`
                        parameter in JSON format. Each item in the JSON array must have
                        a `product_id` (int) and `quantity` (int).
        :return: JsonResponse containing the calculated details of individual items
                 (e.g., `product_id`, `product_name`, `quantity`, `unit_price`,
                 `subtotal`) and the overall total price as a string. If any error
                 occurs (e.g., invalid data or missing product), it returns an error
                 message with the appropriate HTTP status code (e.g., 400, 404).
        """
        try:
            items_json = request.GET.get("items", "[]")
            items_data = json.loads(items_json)

            total = 0
            items_with_prices = []

            for item in items_data:
                product = Product.objects.get(id=item["product_id"])
                quantity = int(item["quantity"])
                subtotal = product.price * quantity
                total += subtotal

                items_with_prices.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "quantity": quantity,
                    "unit_price": str(product.price),
                    "subtotal": str(subtotal)
                })

            return JsonResponse({
                "success": True,
                "items": items_with_prices,
                "total": str(total)
            })

        except Product.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Продукт не знайдено"
            }, status=404)
        except (json.JSONDecodeError, KeyError, ValueError):
            return JsonResponse({
                "success": False,
                "error": "Невірний формат даних"
            }, status=400)


def serialize_order(order):
    """
    Serializes an order object into a dictionary representation suitable for
    serialization or transport. The serialization includes details about the
    order, its client, items, delivery, status, and status history.

    :param order: The order object to serialize.
    :type order: Order
    :return: A dictionary representation of the order object.
    :rtype: dict
    """
    from datetime import date, datetime, time

    def serialize_datetime(dt):
        if dt is None:
            return None
        if isinstance(dt, (date, datetime, time)):
            return dt.isoformat()
        return str(dt)

    items_data = [
        {
            "id": item.id,
            "product": {
                "id": item.product.id,
                "name": item.product.name,
                "emoji": getattr(item.product, "emoji", "🌹"),
                "price": str(item.product.price)
            },
            "quantity": item.quantity,
            "unit_price": str(item.unit_price),
            "subtotal": str(item.subtotal)
        }
        for item in order.items.select_related("product").all()
    ]

    history_data = [
        {
            "id": h.id,
            "from_status": h.from_status,
            "to_status": h.to_status,
            "from_status_display": h.get_from_status_display(),
            "to_status_display": h.get_to_status_display(),
            "changed_by": h.changed_by.get_full_name() if h.changed_by else "Система",
            "notes": h.notes or "",
            "created_at": serialize_datetime(h.created_at)
        }
        for h in order.status_history.select_related("changed_by").all()
    ]

    return {
        "id": order.id,
        "client": {
            "id": order.client.id,
            "full_name": order.client.full_name,
            "first_name": order.client.first_name,
            "last_name": order.client.last_name,
            "phone": order.client.phone
        },
        "items": items_data,
        "total_price": str(order.total_price),
        "needs_delivery": order.needs_delivery,
        "delivery_address": order.delivery_address or "",
        "delivery_date": serialize_datetime(order.delivery_date),
        "delivery_time": serialize_datetime(order.delivery_time),
        "status": order.status,
        "status_display": order.get_status_display(),
        "notes": order.notes or "",
        "status_history": history_data
    }
