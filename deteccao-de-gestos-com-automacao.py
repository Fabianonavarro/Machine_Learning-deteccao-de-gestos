import cv2
import numpy as np
import math
import os
import time

# Função para executar o programa com base no gesto detectado
def executar_programa(gesto):
    comandos = {
        1: 'start winword',  # Microsoft Word
        2: 'start excel',    # Microsoft Excel
        3: 'start powerpnt', # Microsoft PowerPoint
        4: 'start firefox',  # Firefox
        5: 'start spyder',   # Spyder IDE
        6: 'cmd /k echo Reposition'  # Mensagem de reposição
    }
    comando = comandos.get(gesto, '')
    if comando:
        os.system(comando)

# Função para detectar se a mão está fechada
def detectar_mao_fechada(mask):
    # O valor de 2000 é um limite que pode ser ajustado conforme necessário
    return np.sum(mask) < 2000

# Inicialização da captura de vídeo
cap = cv2.VideoCapture(0)

ultimo_gesto = None
tempo_ultimo_gesto = time.time()
tempo_ultimo_executado = time.time()

while True:
    try:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        kernel = np.ones((3, 3), np.uint8)

        # Define a região de interesse
        roi = frame[100:300, 100:300]
        cv2.rectangle(frame, (100, 100), (300, 300), (0, 255, 0), 0)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Definir gama de cor da pele em HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)

        # Extrair imagem do contorno da pele
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        mask = cv2.dilate(mask, kernel, iterations=4)
        mask = cv2.GaussianBlur(mask, (5, 5), 100)

        # Encontrando os contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            cnt = max(contours, key=cv2.contourArea)
            epsilon = 0.0005 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            hull = cv2.convexHull(cnt)
            areahull = cv2.contourArea(hull)
            areacnt = cv2.contourArea(cnt)
            arearatio = ((areahull - areacnt) / areacnt) * 100

            hull = cv2.convexHull(approx, returnPoints=False)
            defects = cv2.convexityDefects(approx, hull)
            l = 0

            if defects is not None:
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(approx[s][0])
                    end = tuple(approx[e][0])
                    far = tuple(approx[f][0])

                    a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                    b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                    c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                    s = (a + b + c) / 2
                    ar = math.sqrt(s * (s - a) * (s - b) * (s - c))
                    d = (2 * ar) / a
                    angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

                    if angle <= 90 and d > 30:
                        l += 1
                        cv2.circle(roi, far, 3, [255, 0, 0], -1)
                    cv2.line(roi, start, end, [0, 255, 0], 2)

            l += 1

            # Determina o gesto detectado
            gesto_detectado = None
            if detectar_mao_fechada(mask):
                cv2.putText(frame, 'Mão Fechada - Fechando...', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
                break  # Sai do loop para fechar o programa
            elif l == 1:
                if areacnt < 2000:
                    cv2.putText(frame, 'Esperando dados', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
                else:
                    if arearatio < 12:
                        gesto_detectado = 1
                        cv2.putText(frame, '1 = Word', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    elif arearatio < 17.5:
                        gesto_detectado = 2
                        cv2.putText(frame, '2 = Excel', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    else:
                        gesto_detectado = 3
                        cv2.putText(frame, '3 = Power Point', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
            elif l == 2:
                gesto_detectado = 2
                cv2.putText(frame, '2 = Excel', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
            elif l == 3:
                if arearatio < 27:
                    gesto_detectado = 3
                    cv2.putText(frame, '3 = Power Point', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
                else:
                    cv2.putText(frame, 'ok', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
            elif l == 4:
                gesto_detectado = 4
                cv2.putText(frame, '4 = Firefox', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
            elif l == 5:
                gesto_detectado = 5
                cv2.putText(frame, '5 = Spyder', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
            elif l == 6:
                gesto_detectado = 6
                cv2.putText(frame, 'Reposition', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
            else:
                cv2.putText(frame, 'Reposition', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)

            # Controle para garantir que o comando é executado após o gesto ser detectado por um período
            if gesto_detectado is not None:
                if gesto_detectado != ultimo_gesto:
                    tempo_ultimo_gesto = time.time()
                    ultimo_gesto = gesto_detectado
                elif time.time() - tempo_ultimo_gesto > 1:  # Espera por 1 segundo após o gesto ser detectado
                    if time.time() - tempo_ultimo_executado > 5:  # Espera 5 segundos antes de executar um novo comando
                        executar_programa(gesto_detectado)
                        tempo_ultimo_executado = time.time()

        # Exibir a imagem
        cv2.imshow('Hand Gesture Detection', frame)

        # Interromper o loop quando a tecla 'q' é pressionada
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        print(f'Erro: {e}')

# Libere o recurso da captura e feche todas as janelas
cap.release()
cv2.destroyAllWindows()
