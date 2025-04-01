import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import os
import sys

# Caminho absoluto onde o executável está rodando
CAMINHO_BASE = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

# Variável global pra guardar o caminho escolhido
pasta_destino = ""

def escolher_pasta():
    global pasta_destino
    pasta = filedialog.askdirectory()
    if pasta:
        pasta_destino = pasta
        label_pasta.config(text=f"Pasta selecionada: {pasta}")
        btn_baixar.config(state=tk.NORMAL)

def baixar_video():
    global pasta_destino
    url = entry_url.get()
    if not url:
        messagebox.showerror("Erro", "Por favor, cole a URL do vídeo.")
        return

    btn_baixar.config(state=tk.DISABLED)
    label_status.config(text="Iniciando download...")
    progress_bar['value'] = 0
    janela.update_idletasks()

    def my_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percent = int(downloaded * 100 / total)
                progress_bar['value'] = percent
                label_status.config(text=f"Baixando... {percent}%")
                janela.update_idletasks()
        elif d['status'] == 'finished':
            label_status.config(text="Finalizando...")

    def download():
        try:
            import sys
            CREATE_NO_WINDOW = 0x08000000

            os.makedirs(pasta_destino, exist_ok=True)
            video_path = os.path.join(pasta_destino, '%(title)s.%(ext)s')

            # Caminho absoluto do yt-dlp.exe (ao lado do .exe principal)
            yt_dlp_path = os.path.join(os.path.dirname(sys.executable), "yt-dlp.exe")

            comando = [
                yt_dlp_path,
                '--no-check-certificate',
                '-f', 'best[ext=mp4][vcodec^=avc1]',
                '-o', video_path,
                url
            ]

            processo = subprocess.Popen(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )

            saida_completa = ""

            for linha in processo.stdout:
                saida_completa += linha
                if "[download]" in linha and "%" in linha:
                    try:
                        parte = linha.strip().split("[download]")[1]
                        if "%" in parte:
                            percentual = parte.strip().split("%")[0]
                            percentual = float(percentual.strip())
                            progress_bar['value'] = percentual
                            label_status.config(text=f"Baixando... {percentual:.1f}%")
                            janela.update_idletasks()
                    except:
                        pass  # ignora erro de parsing

            processo.wait()

            if processo.returncode == 0:
                label_status.config(text="Download concluído ✅")
                messagebox.showinfo("Sucesso", f"Vídeo salvo em:\n{pasta_destino}")
            else:
                raise Exception(f"O yt-dlp retornou erro:\n\n{saida_completa.strip()}")

        except Exception as e:
            messagebox.showerror("Erro no download", str(e))
            label_status.config(text="Erro ao baixar")

        finally:
            btn_baixar.config(state=tk.NORMAL)
            progress_bar['value'] = 100

    threading.Thread(target=download).start()

# Interface gráfica
janela = tk.Tk()
janela.title("Baixar Vídeo do YouTube")
janela.geometry("480x270")

tk.Label(janela, text="1. Escolha onde salvar o vídeo:").pack(pady=5)
btn_pasta = tk.Button(janela, text="Selecionar pasta", command=escolher_pasta)
btn_pasta.pack()

label_pasta = tk.Label(janela, text="Nenhuma pasta selecionada")
label_pasta.pack(pady=5)

tk.Label(janela, text="2. Cole a URL do YouTube:").pack(pady=5)
entry_url = tk.Entry(janela, width=55)
entry_url.pack(pady=5)

btn_baixar = tk.Button(janela, text="Baixar Vídeo", command=baixar_video)
btn_baixar.pack(pady=10)
btn_baixar.config(state=tk.DISABLED)  # desabilitado até a pasta ser escolhida

progress_bar = ttk.Progressbar(janela, orient='horizontal', length=360, mode='determinate')
progress_bar.pack(pady=5)

label_status = tk.Label(janela, text="")
label_status.pack()

janela.mainloop()
