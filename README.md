# PyAte (Python Authenticator Token Extractor)

PYATE adalah aplikasi Command-Line Interface (CLI) yang ringan dan efisien, dibuat dengan Python, yang berfungsi sebagai pengganti Google Authenticator. Aplikasi ini memungkinkan Anda mengelola dan menghasilkan Time-based One-Time Passwords (TOTP) untuk berbagai akun langsung dari terminal Anda.
Alih-alih memindai kode QR secara manual, PYATE membaca daftar alamat otpauth:// dari sebuah file teks (accounts.txt). 
Ini memungkinkan Anda mengelola banyak akun secara bersamaan.

## Fitur Unggulan
* **Dukungan Multi-Akun**: Kelola beberapa akun TOTP dari satu tempat dengan daftar yang sederhana di file teks.
* **Tampilan CLI yang Bersih**: Output terminal diperbarui secara otomatis setiap 30 detik untuk menampilkan kode OTP yang selalu valid.
* **Pembaruan Waktu yang Dinamis**: Hitungan mundur sisa waktu diperbarui setiap detik di baris yang sama, memberikan pengalaman yang mirip dengan aplikasi aslinya.
* **Pembersihan Layar Otomatis**: Layar terminal dibersihkan dan diperbarui sepenuhnya saat kode OTP berganti, memastikan tidak ada teks lama yang tertinggal.
* **Salin Otomatis**: Kode OTP untuk akun pertama secara otomatis disalin ke clipboard untuk memudahkan penempelan.
* **Kompatibilitas Lintas Platform**: Bekerja dengan baik di Windows, macOS, dan Linux.

## Fitur Tambahan (Berbasis Argumen)
PyAte telah diperbarui untuk menyertakan fitur berbasis argumen, memberikan lebih banyak kontrol dan fleksibilitas.

## Cara Penggunaan
Pastikan Anda sudah menginstal pustaka yang diperlukan.

```bash
pip install -r requirements.txt
```

> Buat File Akun: Buat file bernama accounts.txt di direktori yang sama dengan program. Masukkan alamat otpauth:// untuk setiap akun di baris terpisah.

### Contoh isi accounts.txt
otpauth://totp/Google%3Ayour-email?secret=YOUR_SECRET_KEY&issuer=Google
<br>otpauth://totp/GitHub:your-username?secret=ANOTHER_SECRET_KEY&issuer=GitHub

## Jalankan Aplikasi:

### Mode Normal
Menampilkan semua OTP dan menyalin OTP pertama secara otomatis.

```bash
python pyate.py
```

### Mode Interaktif
Pilih akun mana yang OTP-nya akan disalin.

```bash
python pyate.py --interactive
```

### Mode Pencarian
Tampilkan OTP hanya untuk akun yang cocok.

```bash
python pyate.py --search "google"
```

### Gunakan File Kustom

```bash
python pyate.py --read auth.txt
```

### Lihat Halaman Bantuan

```bash
python pyate.py --help
```