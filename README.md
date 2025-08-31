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
* **Impor Migrasi**: Otomatis mengimpor semua akun dari kode QR migrasi Google Authenticator, menyederhanakan proses penyiapan.

## Fitur Tambahan (Berbasis Argumen)
PyAte telah diperbarui untuk menyertakan fitur berbasis argumen, memberikan lebih banyak kontrol dan fleksibilitas.

## Cara Penggunaan
Pastikan Anda sudah menginstal pustaka yang diperlukan.

```bash
pip install -r requirements.txt
```

> Buat File Akun: Buat file bernama accounts.txt di direktori yang sama dengan program. Masukkan alamat otpauth:// untuk setiap akun di baris terpisah.

### Contoh isi accounts.txt

```
otpauth://totp/GitHub:your-username?secret=ANOTHER_SECRET_KEY&issuer=GitHub
```

## Jalankan Aplikasi:

### Mode Normal
Menampilkan semua OTP dan menyalin OTP pertama secara otomatis.

```bash
python pyate.py
```

### Import Migration
Fitur ini memungkinkan Anda mengimpor banyak akun TOTP sekaligus dari kode QR migrasi Google Authenticator. Ini sangat berguna ketika Anda ingin mentransfer semua akun dari aplikasi Google Authenticator di ponsel Anda.

```bash
python pyate.py --import-migration path/to/qrcode.png
```
--import-migration: Gunakan argumen ini diikuti dengan jalur file gambar dari kode QR migrasi. PyAte akan memindai gambar, mengekstrak semua URI OTP, dan menambahkannya ke file accounts.txt.

### Menyimpan ke File Kustom
Anda bisa mengombinasikan --import-migration dengan --output-file untuk menyimpan URI yang diimpor ke file yang berbeda, seperti new_accounts.txt.

```bash
python pyate.py --import-migration path/to/qrcode.png --output-file new_accounts.txt
```

### Generate YubiKey Manager (ykman) Commands

Fitur ini mengubah URI migrasi yang diekstrak dari kode QR atau URI langsung menjadi perintah `ykman` yang siap dijalankan. 

Ini sangat ideal untuk pengguna yang ingin mengimpor akun TOTP mereka dari Google Authenticator langsung ke perangkat YubiKey.

```bash
python pyate.py --generate-ykman path/to/qrcode.png
```
Perintah ini akan memindai kode QR, mengekstrak URI OTP, dan mencetak serangkaian perintah `ykman` ke terminal. 

Anda dapat langsung menyalin dan menempelkan perintah tersebut untuk mengimpor akun Anda ke YubiKey.

### Mode Interaktif
Pilih akun mana yang OTP-nya akan disalin.

```bash
python pyate.py --interactive
```

### Mode Pencarian
Argumen `--search` memungkinkan Anda untuk memfilter akun dan hanya menampilkan OTP untuk akun yang cocok dengan kata kunci yang Anda masukkan. Ini sangat berguna ketika Anda memiliki banyak akun dalam file Anda dan hanya ingin melihat satu atau beberapa akun tertentu.

```bash
python pyate.py --search "google"
```

**Contoh**: Jika file accounts.txt Anda berisi akun untuk Google dan GitHub, perintah python pyate.py --search "google" akan memfilter daftar dan hanya menampilkan OTP untuk akun Google. Perintah ini akan menampilkan output seperti ini:

```
1 accounts loaded from 'accounts.txt'.

[Google: your-email] OTP: 123456

Remaining Time: 25s
```

### Gunakan File Kustom
Secara default, PyAte akan membaca akun dari file accounts.txt. Namun, dengan argumen --read, Anda dapat menentukan file teks lain untuk memuat akun OTP. Ini memungkinkan Anda untuk mengelola beberapa set akun secara terpisah tanpa harus mengubah file utama.

**Contoh**: Jika Anda memiliki file bernama auth.txt dan ingin PyAte memuat akun dari sana, gunakan perintah:

```bash
python pyate.py --read auth.txt
```

### Lihat Halaman Bantuan
Argumen --help menampilkan deskripsi singkat tentang program dan semua argumen yang tersedia, lengkap dengan penjelasannya. Ini adalah cara cepat untuk mendapatkan ringkasan semua fitur yang didukung oleh PyAte langsung di terminal Anda.

**Contoh**
```bash
python pyate.py --help
```
