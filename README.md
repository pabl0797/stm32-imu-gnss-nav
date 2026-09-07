# stm32-imu-gnss-nav
Proyecto personal para aprendizaje de uso de perisféricos GPS, IMU y si implementación conjunta



Lista de problemas:
1º Una vez funciona el módulo de GPS a la hora de leer las tramas devido al bucle while para imprimir por pantalla, el uso de interrupciones para la lectura del GPS y el uso de un solo buffer para guardar la información que proviene de la interrupción generada por el GPS, a la hora de imprimir todo en el bucle while no le da tiempo a que se imprima todo antes de que se empiece a escrivir más información en el buffer compartido para grabar y escribir, por lo que antes de terminar de imprimir la última trama se imprime tambien el principio de la siguiente lo que genera ruido visual he imposivilidad de tratar esas tramas para nada:



Lista de soluciones:
1º Se va a implementar un segundo buffer el cual se va a usar para escribir para que se queden separados completamnete esos bloques y voy a intentar agilizar la función de imprimir para que no sea tán lenta y lo pueda seguir usando como método de depuración
