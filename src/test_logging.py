from custom_logger import CustomLogger
from audit_decorators import audit, audit_async, audit_async_task
import asyncio, logging

# Configurar el logging
custom_level_formats = {
    logging.DEBUG: "[%(asctime)s] [%(levelname)s] [%(audit_path)s] %(message)s",
    logging.ERROR: "[%(asctime)s] [%(levelname)s] [%(audit_path)s] %(message)s",
}

CustomLogger.setup_custom_logging(output_format="colored", level_formats=custom_level_formats, logger_name="logcleanaudit", loki=True)

# Función sincrónica con el decorador @audit
@audit
def test_function(a, b):
    return a + b

# Función asíncrona con el decorador @audit_async
@audit_async
async def async_test_function(a, b):
    await asyncio.sleep(1)
    return a + b

# Función asíncrona que crea una tarea con el decorador @audit_async_task
@audit_async_task
async def async_task_test_function(a, b):
    await asyncio.sleep(1)
    return a * b

# Ejecuta las funciones de prueba
result_sync = test_function(2, 3)
print(f"Result of test_function: {result_sync}")

async def main():
    result_async = await async_test_function(2, 3)
    print(f"Result of async_test_function: {result_async}")

    result_async_task = await async_task_test_function(2, 3)
    print(f"Result of async_task_test_function: {result_async_task}")

asyncio.run(main())