import streamlit as st
from yt_dlp import YoutubeDL
import tempfile
import os

st.title("Baixador de vídeos do Youtube (liste todos os vídeos por linha)")
arquivo_cookie = st.file_uploader("Arquivo cookies.txt")

video_txt_area = st.text_area("Link(s) do(s) vídeo(s)", height=200)
URLS = video_txt_area.split("\n")
formato_escolha = st.radio("Escolha o formato:", ["MP4 (Vídeo Melhor Qualidade)", "MP3 (Apenas Áudio)"])
baixar_button = st.button("Baixar")



if baixar_button and arquivo_cookie:
    if not arquivo_cookie:
        st.warning("Arquivo cookie necessário! Leia a documentação para saber onde adquirir.")
    else:
        # 1. Escreve os bytes do upload em um arquivo temporário no disco
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(arquivo_cookie.getvalue())
            caminho_temp = tmp.name
        formatacao = {}
        if formato_escolha == "MP4 (Vídeo Melhor Qualidade)":
            formatacao = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Apenas a palavra best, sem símbolos ou barras
                'outtmpl': '%(title)s.%(ext)s',
                'cookiefile': caminho_temp,
                'js_runtimes': {'node': {}},          # Força o yt-dlp a usar o Node.js
                'remote_components': ['ejs:github'],
            }
            
        elif formato_escolha == "MP3 (Apenas Áudio)":
            formatacao = {
                "format":"bestaudio/best",
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192', # Qualidade do mp3 (192kbps)
                }],
                "outtmpl":"%(title)s.%(ext)s",
                'cookiefile': caminho_temp,
                'js_runtimes': {'node': {}},          # Força o yt-dlp a usar o Node.js
                'remote_components': ['ejs:github'],
            }
        try:
            with YoutubeDL(formatacao) as ydl:
                ydl.download(URLS)
                baixar_button = False        
                st.success("Download concluído com sucesso!")
            
        except Exception as e:
            st.error(f"Ocorreu um erro durante o download: {e}")
