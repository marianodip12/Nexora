from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, Optional
import json

class RestaurantConversationInput(BaseModel):
    """Input schema for Restaurant Conversation Handler Tool."""
    user_message: str = Field(..., description="The user's message in the conversation")
    conversation_state: Optional[str] = Field(default="initial", description="Current conversation state (initial, menu, ordering, confirming, etc.)")

class RestaurantConversationHandlerTool(BaseTool):
    """Tool for handling Spanish restaurant conversations with intent detection and state management."""

    name: str = "restaurant_conversation_handler"
    description: str = (
        "Processes Spanish restaurant conversations, detects intents, manages ordering flow, "
        "and returns structured responses with conversation state management. Handles greetings, "
        "menu display, ordering process, business hours, and human transfer requests."
    )
    args_schema: Type[BaseModel] = RestaurantConversationInput

    def _get_menu_items(self) -> Dict[str, Dict[str, Any]]:
        """Returns the restaurant menu with items and prices."""
        return {
            "1": {"name": "Pizza Margherita", "price": 15.50, "description": "Tomate, mozzarella, albahaca fresca"},
            "2": {"name": "Pasta Carbonara", "price": 12.80, "description": "Pasta con huevo, panceta, queso parmesano"},
            "3": {"name": "Ensalada César", "price": 9.90, "description": "Lechuga, pollo, crutones, salsa césar"},
            "4": {"name": "Hamburguesa Clásica", "price": 11.50, "description": "Carne, lechuga, tomate, cebolla, queso"},
            "5": {"name": "Paella Valenciana", "price": 18.90, "description": "Arroz con pollo, conejo, garrofón, judías verdes"},
            "6": {"name": "Salmón a la Plancha", "price": 16.70, "description": "Salmón fresco con verduras al vapor"},
            "7": {"name": "Tiramisu", "price": 6.50, "description": "Postre italiano con café y mascarpone"},
            "8": {"name": "Bebidas", "price": 2.50, "description": "Agua, refrescos, cerveza, vino"}
        }

    def _detect_intent(self, message: str, current_state: str) -> str:
        """Detects the user's intent from their message."""
        message_lower = message.lower().strip()
        
        # Menu intent
        if message_lower in ["1", "ver menú", "ver menu", "menu", "menú", "carta"]:
            return "show_menu"
        
        # Ordering intent
        elif message_lower in ["2", "hacer pedido", "pedido", "pedir", "ordenar"]:
            return "start_ordering"
        
        # Business hours intent
        elif message_lower in ["3", "consultar horario", "horario", "horarios", "cuando abren", "horas"]:
            return "show_hours"
        
        # Human transfer intent
        elif message_lower in ["4", "hablar con humano", "humano", "operador", "ayuda humana"]:
            return "transfer_human"
        
        # Menu item selection during ordering
        elif current_state == "ordering" and message_lower.isdigit():
            return "select_item"
        
        # Quantity selection
        elif current_state == "selecting_quantity" and message_lower.isdigit():
            return "select_quantity"
        
        # Confirmation responses
        elif current_state == "confirming_order":
            if message_lower in ["sí", "si", "confirmar", "correcto", "ok"]:
                return "confirm_order"
            elif message_lower in ["no", "cancelar", "cambiar"]:
                return "cancel_order"
        
        # Continue ordering
        elif current_state == "item_added":
            if message_lower in ["sí", "si", "más", "mas", "continuar"]:
                return "continue_ordering"
            elif message_lower in ["no", "finalizar", "terminar", "listo"]:
                return "finish_ordering"
        
        # Default to greeting for any other message
        return "greeting"

    def _generate_response(self, intent: str, message: str, current_state: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generates appropriate response based on detected intent."""
        
        if intent == "greeting":
            response_text = (
                "¡Bienvenido/a a Restaurante Casa Bella! 🍽️\n\n"
                "¿En qué puedo ayudarle hoy?\n\n"
                "1️⃣ Ver menú\n"
                "2️⃣ Hacer pedido\n"
                "3️⃣ Consultar horario\n"
                "4️⃣ Hablar con un humano\n\n"
                "Por favor, seleccione una opción (1-4) o escriba su preferencia."
            )
            return {
                "response_text": response_text,
                "next_conversation_state": "main_menu",
                "intent_detected": "greeting",
                "requires_human_transfer": False
            }

        elif intent == "show_menu":
            menu_items = self._get_menu_items()
            menu_text = "🍽️ **MENÚ CASA BELLA** 🍽️\n\n"
            
            for item_id, item_info in menu_items.items():
                menu_text += f"{item_id}. **{item_info['name']}** - €{item_info['price']:.2f}\n"
                menu_text += f"   {item_info['description']}\n\n"
            
            menu_text += "¿Desea hacer un pedido? Escriba '2' o 'hacer pedido'"
            
            return {
                "response_text": menu_text,
                "next_conversation_state": "menu_displayed",
                "intent_detected": "show_menu",
                "requires_human_transfer": False
            }

        elif intent == "start_ordering":
            menu_items = self._get_menu_items()
            menu_text = "🛒 **REALIZAR PEDIDO** 🛒\n\n"
            
            for item_id, item_info in menu_items.items():
                menu_text += f"{item_id}. {item_info['name']} - €{item_info['price']:.2f}\n"
            
            menu_text += "\nPor favor, seleccione el número del producto que desea pedir (1-8):"
            
            # Initialize order context
            if "order" not in context:
                context["order"] = []
            
            return {
                "response_text": menu_text,
                "next_conversation_state": "ordering",
                "intent_detected": "start_ordering",
                "requires_human_transfer": False
            }

        elif intent == "select_item":
            item_number = message.strip()
            menu_items = self._get_menu_items()
            
            if item_number in menu_items:
                selected_item = menu_items[item_number]
                context["current_item"] = {
                    "id": item_number,
                    "name": selected_item["name"],
                    "price": selected_item["price"]
                }
                
                response_text = (
                    f"Ha seleccionado: **{selected_item['name']}** - €{selected_item['price']:.2f}\n\n"
                    f"{selected_item['description']}\n\n"
                    "¿Cuántas unidades desea? (Escriba un número del 1 al 10)"
                )
                
                return {
                    "response_text": response_text,
                    "next_conversation_state": "selecting_quantity",
                    "intent_detected": "select_item",
                    "requires_human_transfer": False
                }
            else:
                return {
                    "response_text": "Opción no válida. Por favor, seleccione un número del 1 al 8.",
                    "next_conversation_state": "ordering",
                    "intent_detected": "select_item",
                    "requires_human_transfer": False
                }

        elif intent == "select_quantity":
            try:
                quantity = int(message.strip())
                if 1 <= quantity <= 10:
                    current_item = context.get("current_item", {})
                    if current_item:
                        # Add item to order
                        order_item = {
                            "name": current_item["name"],
                            "price": current_item["price"],
                            "quantity": quantity,
                            "total": current_item["price"] * quantity
                        }
                        
                        if "order" not in context:
                            context["order"] = []
                        context["order"].append(order_item)
                        
                        response_text = (
                            f"✅ Agregado: {quantity} x {current_item['name']} - €{order_item['total']:.2f}\n\n"
                            "¿Desea agregar algo más?\n"
                            "• Escriba 'sí' para continuar pidiendo\n"
                            "• Escriba 'no' para finalizar el pedido"
                        )
                        
                        return {
                            "response_text": response_text,
                            "next_conversation_state": "item_added",
                            "intent_detected": "select_quantity",
                            "requires_human_transfer": False
                        }
                else:
                    return {
                        "response_text": "Cantidad no válida. Por favor, escriba un número del 1 al 10.",
                        "next_conversation_state": "selecting_quantity",
                        "intent_detected": "select_quantity",
                        "requires_human_transfer": False
                    }
            except ValueError:
                return {
                    "response_text": "Por favor, escriba un número válido del 1 al 10.",
                    "next_conversation_state": "selecting_quantity",
                    "intent_detected": "select_quantity",
                    "requires_human_transfer": False
                }

        elif intent == "continue_ordering":
            return self._generate_response("start_ordering", message, current_state, context)

        elif intent == "finish_ordering":
            order = context.get("order", [])
            if not order:
                return {
                    "response_text": "No hay productos en su pedido. ¿Desea comenzar a pedir?",
                    "next_conversation_state": "main_menu",
                    "intent_detected": "finish_ordering",
                    "requires_human_transfer": False
                }
            
            # Generate order summary
            summary_text = "📋 **RESUMEN DE SU PEDIDO** 📋\n\n"
            total = 0
            
            for item in order:
                summary_text += f"• {item['quantity']} x {item['name']} - €{item['total']:.2f}\n"
                total += item['total']
            
            summary_text += f"\n💰 **TOTAL: €{total:.2f}**\n\n"
            summary_text += (
                "¿Confirma su pedido?\n"
                "• Escriba 'sí' para confirmar\n"
                "• Escriba 'no' para cancelar"
            )
            
            return {
                "response_text": summary_text,
                "next_conversation_state": "confirming_order",
                "intent_detected": "finish_ordering",
                "requires_human_transfer": False
            }

        elif intent == "confirm_order":
            order = context.get("order", [])
            total = sum(item['total'] for item in order)
            
            response_text = (
                "✅ **PEDIDO CONFIRMADO** ✅\n\n"
                f"Total: €{total:.2f}\n"
                "Tiempo estimado de entrega: 25-30 minutos\n\n"
                "Recibirá una confirmación por SMS con el número de seguimiento.\n"
                "¡Gracias por elegir Casa Bella! 🍽️\n\n"
                "¿Necesita algo más?"
            )
            
            # Clear the order context
            context["order"] = []
            
            return {
                "response_text": response_text,
                "next_conversation_state": "order_confirmed",
                "intent_detected": "confirm_order",
                "requires_human_transfer": False
            }

        elif intent == "cancel_order":
            # Clear the order context
            context["order"] = []
            
            return {
                "response_text": (
                    "❌ Pedido cancelado.\n\n"
                    "¿Desea hacer un nuevo pedido o necesita ayuda con algo más?\n\n"
                    "1️⃣ Ver menú\n"
                    "2️⃣ Hacer pedido\n"
                    "3️⃣ Consultar horario\n"
                    "4️⃣ Hablar con un humano"
                ),
                "next_conversation_state": "main_menu",
                "intent_detected": "cancel_order",
                "requires_human_transfer": False
            }

        elif intent == "show_hours":
            response_text = (
                "🕒 **HORARIOS DE CASA BELLA** 🕒\n\n"
                "**Lunes a Jueves:**\n"
                "• Almuerzo: 12:00 - 16:00\n"
                "• Cena: 19:00 - 23:30\n\n"
                "**Viernes y Sábado:**\n"
                "• Almuerzo: 12:00 - 16:00\n"
                "• Cena: 19:00 - 00:30\n\n"
                "**Domingo:**\n"
                "• Almuerzo: 12:00 - 16:00\n"
                "• Cena: 19:00 - 23:00\n\n"
                "📞 Para reservas: (+34) 91 234 5678\n"
                "📍 Dirección: Calle Gran Vía 25, Madrid\n\n"
                "¿Puedo ayudarle con algo más?"
            )
            
            return {
                "response_text": response_text,
                "next_conversation_state": "hours_displayed",
                "intent_detected": "show_hours",
                "requires_human_transfer": False
            }

        elif intent == "transfer_human":
            return {
                "response_text": (
                    "🤝 **TRANSFERENCIA A OPERADOR HUMANO** 🤝\n\n"
                    "Le vamos a conectar con uno de nuestros asistentes.\n"
                    "Por favor, espere un momento...\n\n"
                    "Tiempo estimado de espera: 2-3 minutos\n"
                    "Su conversación será transferida con todo el contexto."
                ),
                "next_conversation_state": "human_transfer",
                "intent_detected": "transfer_human",
                "requires_human_transfer": True
            }

        else:
            return {
                "response_text": (
                    "No entendí su mensaje. ¿Puede reformularlo?\n\n"
                    "Opciones disponibles:\n"
                    "1️⃣ Ver menú\n"
                    "2️⃣ Hacer pedido\n"
                    "3️⃣ Consultar horario\n"
                    "4️⃣ Hablar con un humano"
                ),
                "next_conversation_state": "main_menu",
                "intent_detected": "unknown",
                "requires_human_transfer": False
            }

    def _run(self, user_message: str, conversation_state: Optional[str] = "initial") -> str:
        """Main method to process restaurant conversations."""
        
        try:
            # Initialize context from conversation state
            context = {}
            if conversation_state and conversation_state != "initial":
                try:
                    # In a real implementation, you might load context from a database
                    # For now, we'll maintain a simple context per session
                    context = {}
                except:
                    context = {}
            
            # Detect intent
            intent = self._detect_intent(user_message, conversation_state or "initial")
            
            # Generate response
            response = self._generate_response(intent, user_message, conversation_state or "initial", context)
            
            # Return JSON response
            return json.dumps(response, ensure_ascii=False, indent=2)
            
        except Exception as e:
            # Error handling
            error_response = {
                "response_text": (
                    "Lo siento, ha ocurrido un error técnico. "
                    "¿Puede intentarlo de nuevo o prefiere hablar con un humano?"
                ),
                "next_conversation_state": "error",
                "intent_detected": "error",
                "requires_human_transfer": False
            }
            return json.dumps(error_response, ensure_ascii=False, indent=2)