import requests
import os

def generate_image(host_url, api_key, prompt):
    """
    Fungsi untuk mengirim permintaan ke AI Stable Diffusion WebUI untuk menghasilkan gambar.
    
    Args:
        host_url (str): URL host dari AI Stable Diffusion WebUI.
        api_key (str): API key untuk otentikasi.
        prompt (str): Prompt yang digunakan untuk menghasilkan gambar.
        
    Returns:
        bytes: Data gambar yang dihasilkan.
    """
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.post(f"{host_url}/api/generate", json={"prompt": prompt}, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to generate image: {response.status_code}, {response.text}")

def save_image(image_data, path):
    """
    Fungsi untuk menyimpan data gambar ke file.
    
    Args:
        image_data (bytes): Data gambar.
        path (str): Path tempat menyimpan gambar.
    """
    with open(path, "wb") as f:
        f.write(image_data)

def input_prompt():
    """
    Fungsi generator yang meminta input prompt dari pengguna.
    """
    while True:
        prompt = input("Masukkan prompt untuk generate image: ")
        if prompt.lower() == 'kembangkan':
            continue
        elif prompt.lower() == 'keluar':
            print("Terima kasih telah menggunakan layanan ini. Sampai jumpa!")
            break
        yield prompt

def main():
    host_url = input("Masukkan host URL untuk AI Stable Diffusion WebUI: ")
    api_key = input("Masukkan API key: ")
    image_path = "image.png"
    
    for prompt in input_prompt():
        if prompt.lower() == 'keluar':
            break
        
        try:
            print(f"Menghasilkan gambar untuk prompt: {prompt}")
            image_data = generate_image(host_url, api_key, prompt)
            save_image(image_data, image_path)
            print(f"Gambar telah disimpan ke {image_path}")
            
            export_path = input("Masukkan direktori untuk ekspor gambar yang telah selesai: ")
            if not os.path.isdir(export_path):
                os.makedirs(export_path)
            
            export_image_path = os.path.join(export_path, image_path)
            os.rename(image_path, export_image_path)
            print(f"Gambar telah diekspor ke {export_image_path}")
            
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
