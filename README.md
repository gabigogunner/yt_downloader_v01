# 🎬 Baixador de Vídeos do YouTube

App simples pra baixar vídeos do YouTube em **MP4** ou extrair só o áudio em **MP3**, direto do navegador — sem instalar nada.

## 🔗 Acesse aqui

### 👉 [yt-downloader-gunner.streamlit.app](https://yt-downloader-gunner.streamlit.app/)

Não precisa instalar nada, criar conta ou ter conhecimento técnico. É só abrir o link.

---

## 📝 Como usar

1. **Cole o link do vídeo** na caixa de texto
   Quer baixar mais de um? Cole um link por linha:
   ```
   https://www.youtube.com/watch?v=xxxxxxxxxxx
   https://www.youtube.com/watch?v=yyyyyyyyyyy
   ```

2. **Escolha o formato:**
   - **MP4** → baixa o vídeo completo, na melhor qualidade
   - **MP3** → baixa só o áudio

3. **Clique em "Processar Vídeo"** e aguarde. Quando terminar, vai aparecer um botão pra baixar o arquivo (ou um `.zip`, se você colou mais de um link).

### 🍪 O vídeo pede login ou dá erro de "vídeo indisponível"?

Alguns vídeos (privados, com restrição de idade, ou que o YouTube decide bloquear) só baixam se você enviar seus cookies do YouTube:

1. Instale uma extensão de exportar cookies no navegador — ex: [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) (Chrome/Edge)
2. Entre em [youtube.com](https://youtube.com) logado na sua conta
3. Clique na extensão e exporte/baixe o arquivo `cookies.txt`
4. No app, clique em **"Arquivo cookies.txt"** e envie o arquivo que você baixou
5. Cole o link do vídeo normalmente e clique em Processar

> ⚠️ Nunca compartilhe seu `cookies.txt` com outras pessoas — ele dá acesso à sua conta do YouTube/Google. Use só localmente, no próprio app.

---

## ⚖️ Aviso

Use pra baixar conteúdo próprio, de domínio público, ou com autorização de quem detém os direitos. Respeite os [Termos de Serviço do YouTube](https://www.youtube.com/t/terms) e as leis de direitos autorais do seu país.

---

<details>
<summary>🛠️ Informações técnicas (pra quem for mexer no código)</summary>

### Stack
- [Streamlit](https://streamlit.io/) — interface
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (instalado direto do GitHub, sempre atualizado)
- `ffmpeg` via `imageio-ffmpeg` — conversão/merge de áudio e vídeo
- `curl-cffi` — impersonation de navegador (reduz bloqueios do YouTube)
- `yt-dlp-ejs` + `nodejs-wheel` — resolvem os desafios JavaScript que o YouTube exige pra liberar os formatos de vídeo

### `requirements.txt`
```pip-requirements
streamlit
git+https://github.com/yt-dlp/yt-dlp.git
imageio-ffmpeg
curl-cffi
yt-dlp-ejs
nodejs-wheel
```

> Não é necessário Node.js do sistema (`package.txt`) — o `nodejs-wheel` já instala uma versão moderna via pip. O Node do `apt` no Debian costuma ser antigo demais (v18) para o que o `yt-dlp-ejs` exige (v22+).

### Rodar localmente
```bash
git clone <url-do-repositorio>
cd <pasta-do-projeto>
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
streamlit run yt_downloader.py
```

### Problemas comuns
| Sintoma | Causa provável |
|---|---|
| "Requested format is not available" | `yt-dlp-ejs`/`nodejs-wheel` não instalados ou app não reiniciou após mudança no `requirements.txt` |
| "Sign in to confirm you're not a bot" | Precisa de `cookies.txt` válido |
| Erro 403 / falha intermitente | Bloqueio temporário do YouTube — tente de novo em alguns minutos |

Sempre que der erro, abra **"Detalhes técnicos do erro"** dentro do app pra ver a mensagem real do yt-dlp.

</details>
