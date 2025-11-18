import requests
import sys
import json

def make_request(id_servico=None):
    base = "https://servicos.ba.gov.br/api/servicossecretaria/17"
    url = f"{base}/{id_servico}" if id_servico else base
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=2)
    session.mount("https://", adapter)

    try:
        resp = session.get(url, timeout=10, headers={"Accept": "application/json"})
    except requests.RequestException as e:
        print(f"Erro de rede: {e}")
        return None

    if resp.status_code == 200:
        return resp.json()
    else:
        # Mostra o código e parte do corpo para ajudar no debug
        print(f"Erro ao acessar a API. Código de status: {resp.status_code}")
        print("Resposta (até 2000 chars):")
        print(resp.text[:2000])
        return None

if __name__ == "__main__":
    id_arg = sys.argv[1] if len(sys.argv) > 1 else None
    data = make_request(id_arg)
    if data is not None:
        print(json.dumps(data, ensure_ascii=False, indent=2))