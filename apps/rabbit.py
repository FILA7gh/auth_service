from apps.config import RABBITMQ_URL, QUEUE_NAME
import aio_pika

from apps.schemas import MessageSchema


class Rabbit:
    @classmethod
    async def get_rabbit_connection(cls):
        return await aio_pika.connect_robust(RABBITMQ_URL)

    @classmethod
    async def setup_rabbitmq(cls):
        connection = await cls.get_rabbit_connection()
        async with connection:
            async with connection.channel() as channel:
                await channel.default_exchange.publish(
                    aio_pika.Message(body=b'Hello RabbitMQ'),
                    routing_key=QUEUE_NAME
                )

    @classmethod
    async def send_message(cls, message: MessageSchema) -> None:
        connection = await cls.get_rabbit_connection()
        async with connection:
            async with connection.channel() as channel:
                queue = await channel.declare_queue(QUEUE_NAME, durable=True)
                await channel.default_exchange.publish(
                    aio_pika.Message(body=message.text.encode()),
                    routing_key=QUEUE_NAME
                )
        return None
