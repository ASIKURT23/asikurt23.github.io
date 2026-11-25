# -*- coding: utf-8 -*-
# aSiKuRT PRO IT CONTROL CENTER v18.0
# Windows 10/11 profesyonel IT bakım, teşhis ve yönetim paneli.
#
# Yalnızca standart Python/Tkinter + Windows yerleşik araçlarını kullanır.
# Harici programlar sessizce kurulmaz; yalnızca resmi üretici sayfaları açılır.
# Sistem değiştiren işlemler onay ister ve yönetici yetkisi gerektirir.

import os
import sys
import re
import json
import math
import time
import queue
import ctypes
import shutil
import threading
import traceback
import subprocess
import webbrowser
from pathlib import Path
from tkinter import messagebox, ttk, scrolledtext, simpledialog
import tkinter as tk

APP_NAME = "aSiKuRT PRO IT CONTROL CENTER"
APP_VERSION = "18.0"
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

# --------------------------------------------------------------------------
#  RENK TEMASI
# --------------------------------------------------------------------------
BG = "#080C14"
SIDEBAR = "#0D1422"
PANEL = "#111A2B"
CARD = "#162237"
BTN = "#1B2A42"
HOVER = "#243857"
BORDER = "#263957"
CYAN = "#00E5FF"
GREEN = "#19D38A"
YELLOW = "#F5B942"
RED = "#FF5570"
PURPLE = "#9B7BFF"
BLUE = "#5EA7FF"
WHITE = "#F5F7FA"
MUTED = "#8D9AAF"
TRACK = "#1E2C47"
GRID = "#101B30"
COLORS = {"cyan": CYAN, "green": GREEN, "yellow": YELLOW, "red": RED,
          "purple": PURPLE, "blue": BLUE}

# --------------------------------------------------------------------------
#  EYLEM KAYIT DEFTERİ:  id -> (Başlık, Basit açıklama, Onay gerekir mi)
# --------------------------------------------------------------------------
ACTIONS = {
    # --- Genel ---
    "health_check": ("🩺 Tek tuşla sağlık kontrolü",
        "Disk, bellek, güvenlik ve güncelleme durumuna bakar; sonucu sade bir özetle gösterir.", False),
    "cleanup": ("🧹 Geçici dosyaları temizle",
        "Kullanıcı Temp klasöründeki gereksiz dosyaları siler ve DNS önbelleğini boşaltır. Kişisel dosyalarınıza dokunmaz.", False),
    "cleanup_windows": ("🧽 Windows geçici dosyalarını temizle",
        "Windows'un kendi Temp klasörlerindeki artık dosyaları siler. Kullanımda olanlar atlanır.", True),
    "cleanmgr": ("🗑 Disk Temizleme aracı",
        "Microsoft'un Disk Temizleme penceresini açar; neyin silineceğini siz seçersiniz.", False),
    "wsreset": ("🏪 Mağaza önbelleğini sıfırla",
        "Microsoft Store açılmıyor ya da uygulama indirmiyorsa sorunu çoğunlukla çözer.", False),
    # --- Onarım ---
    "sfc": ("🛠 Bozuk sistem dosyalarını onar (SFC)",
        "Windows'un bozulmuş sistem dosyalarını arar ve otomatik düzeltir. 10-30 dakika sürebilir.", True),
    "dism": ("🧱 Windows görüntüsünü onar (DISM)",
        "SFC'nin çözemediği derin bozulmaları Microsoft sunucularından onarır. İnternet gerekir.", True),
    "dism_check": ("🧪 Windows sağlığını hızlıca sına",
        "Windows görüntüsünde bozulma var mı diye kısa bir kontrol yapar; hiçbir şeyi değiştirmez.", False),
    "restore_point": ("📌 Geri yükleme noktası oluştur",
        "Bir sorun çıkarsa bilgisayarı bugünkü haline döndürebilmeniz için yedek nokta alır.", True),
    "restore_ui": ("♻ Sistem Geri Yükleme'yi aç",
        "Önceden alınmış bir noktaya geri dönmek için Windows'un geri yükleme sihirbazını açar.", False),
    "update_reset": ("🔄 Windows Update'i onar",
        "Güncelleme takılıyor ya da hata veriyorsa indirilen bozuk güncelleme dosyalarını temizler.", True),
    "windows_update": ("⚙ Windows Update ayarlarını aç",
        "Güncellemeleri denetlemek ve yüklemek için Ayarlar sayfasını açar.", False),
    # --- Güvenlik ---
    "defender_update": ("🔄 Virüs tanımlarını güncelle",
        "Microsoft Defender'ın bilinen virüs listesini en yeni sürüme getirir.", False),
    "defender_quick": ("⚡ Hızlı virüs taraması",
        "Virüslerin en sık saklandığı yerleri birkaç dakikada tarar.", False),
    "defender_full": ("🔎 Tam virüs taraması",
        "Tüm diski baştan sona tarar. Saatler sürebilir, bilgisayar yavaşlayabilir.", True),
    "defender_ui": ("🛡 Windows Güvenlik'i aç",
        "Windows'un güvenlik merkezini açar (virüs koruması, güvenlik duvarı, hesap koruması).", False),
    "defender_status": ("📋 Virüs koruması durumu",
        "Antivirüsün açık olup olmadığını ve son güncelleme/tarama zamanını gösterir.", False),
    "mrt": ("▶ Kötü amaçlı yazılım temizleme aracı (MRT)",
        "Microsoft'un yaygın zararlı yazılımları arayıp silen yerleşik aracını açar.", False),
    "mrt_about": ("ℹ MRT hakkında bilgi",
        "MRT aracının komut seçeneklerini ve ne işe yaradığını gösterir.", False),
    "firewall": ("🔐 Gelişmiş güvenlik duvarı",
        "Hangi programların internete çıkabileceğini belirleyen kuralları açar.", False),
    "firewall_status": ("🔥 Güvenlik duvarı açık mı?",
        "Alan, Özel ve Genel ağ profillerinde güvenlik duvarının durumunu listeler.", False),
    "lusrmgr": ("👤 Yerel kullanıcıları yönet",
        "Bilgisayardaki kullanıcı hesaplarını ve gruplarını açar.", False),
    "local_users_list": ("👥 Kullanıcı hesaplarını listele",
        "Bilgisayardaki hesapları, açık/kapalı durumlarını ve son girişlerini gösterir.", False),
    "shares": ("📂 Paylaşılan klasörler",
        "Ağ üzerinden başkalarına açık olan klasörleri listeler. Beklenmedik paylaşım güvenlik riskidir.", False),
    "bitlocker": ("🔒 Disk şifreleme (BitLocker) durumu",
        "Disklerinizin şifreli olup olmadığını gösterir. Laptop kaybında verinizi korur.", False),
    "activation": ("🔑 Windows lisans durumu",
        "Windows'un etkinleştirilmiş (lisanslı) olup olmadığını ve bitiş tarihini gösterir.", False),
    # --- Disk ---
    "diskmgmt": ("💽 Disk Yönetimi",
        "Disk bölümlerini görmek, biçimlendirmek veya harf atamak için Windows aracını açar.", False),
    "disk_info": ("🔎 Disk modeli ve boyutları",
        "Takılı fiziksel disklerin modelini, bağlantı türünü ve boyutunu listeler.", False),
    "disk_ps": ("📊 Disk sağlık durumu",
        "Her diskin 'Sağlıklı' mı yoksa 'Uyarı' mı olduğunu gösterir.", False),
    "drive_space": ("📦 Sürücülerde boş alan",
        "Tüm sürücülerin toplam ve boş alanını gösterir.", False),
    "smart_health": ("❤ Disk ömrü ve sıcaklığı (SMART)",
        "Diskin sağlık, sıcaklık, çalışma saati ve hata sayacını gösterir. Bozulmadan önce uyarır.", False),
    "big_folders": ("🧮 En çok yer kaplayan klasörler",
        "Kullanıcı klasörünüzde diski en çok dolduran klasörleri sıralar. Biraz sürebilir.", False),
    "optimize_c": ("⚡ C: sürücüsünü optimize et",
        "SSD'de TRIM, HDD'de birleştirme yapar. Diski sağlıklı ve hızlı tutar.", True),
    "dfrgui": ("📈 Sürücüleri Optimize Et penceresi",
        "Windows'un disk optimizasyon penceresini açar ve zamanlama ayarı yapmanızı sağlar.", False),
    "diskpart_info": ("💾 Disk ve birim listesi (DiskPart)",
        "Takılı disklerin ve bölümlerin ham listesini gösterir; hiçbir şeyi değiştirmez.", False),
    "drivers": ("🧾 Yüklü sürücüleri listele",
        "Cihaz sürücülerinin adını, sürümünü ve üreticisini gösterir.", False),
    "chkdsk_scan": ("🔍 Disk hatası taraması (CHKDSK /scan)",
        "Dosya sistemini çevrimiçi tarar; bilgisayarı kapatmadan hata arar.", True),
    "chkdsk_fix": ("🧰 Disk hatalarını onar (CHKDSK /f)",
        "Bulunan dosya sistemi hatalarını düzeltir. Gerekirse yeniden başlatmada çalışır.", True),
    "explorer_c": ("📁 C: sürücüsünü aç",
        "Dosya Gezgini'nde C: sürücüsünü açar.", False),
    # --- Performans ---
    "ultimate_performance": ("⚡ Nihai Performans güç planı",
        "En yüksek hız için güç planını açar. Pil ömrünü ve ısıyı artırabilir.", True),
    "power_plans": ("🔋 Güç planlarını listele",
        "Bilgisayardaki güç planlarını ve hangisinin aktif olduğunu gösterir.", False),
    "power_ui": ("⚙ Güç seçenekleri",
        "Uyku, ekran kapanma ve güç planı ayarlarını açar.", False),
    "taskmgr": ("📊 Görev Yöneticisi",
        "Hangi program ne kadar işlemci, bellek ve disk kullanıyor gösterir; takılan programı kapatır.", False),
    "top_processes": ("🧠 En çok bellek kullanan programlar",
        "Belleği en çok dolduran ilk 25 programı sıralar. Yavaşlığın nedenini bulmaya yarar.", False),
    "ram_info": ("🧠 RAM miktarı",
        "Bilgisayarınızdaki toplam bellek miktarını gösterir.", False),
    "ram_test": ("🧬 RAM hata testi",
        "Windows Bellek Tanılama'yı açar. Yeniden başlatıp RAM'i test eder; mavi ekran şüphesinde kullanın.", False),
    "perfmon": ("📈 Performans İzleyici",
        "İşlemci, bellek, disk ve ağ kullanımını ayrıntılı grafiklerle izler.", False),
    "resmon": ("🔬 Kaynak İzleyici",
        "Hangi programın diske ve ağa ne kadar eriştiğini canlı gösterir.", False),
    "startup_ui": ("🚀 Başlangıç programlarını yönet",
        "Windows açılırken çalışan programları kapatarak açılışı hızlandırmanızı sağlar.", False),
    "game_mode": ("🎮 Oyun Modu'nu aç",
        "Oyun sırasında arka plan işlerini azaltarak daha akıcı oyun sağlar.", False),
    "gamebar": ("🎮 Oyun çubuğu ayarları",
        "Xbox Oyun Çubuğu ve kayıt ayarlarını açar.", False),
    "winsat": ("🏁 Windows performans puanı (WinSAT)",
        "İşlemci, bellek, disk ve ekran kartını test eder. Birkaç dakika sürer.", True),
    "battery_report": ("🔋 Pil sağlık raporu",
        "Pilin ne kadar yıprandığını gösteren raporu masaüstüne kaydeder (dizüstü için).", False),
    "energy_report": ("⚡ Enerji verimliliği raporu",
        "60 saniye izleyip pil ve güç sorunlarını masaüstüne rapor eder.", True),
    # --- Ağ ---
    "wifi_scan": ("📡 Çevredeki Wi-Fi ağlarını tara",
        "Yakındaki kablosuz ağları, sinyal gücünü ve kanallarını listeler.", False),
    "wifi_profiles": ("📋 Kayıtlı Wi-Fi ağları",
        "Bu bilgisayarın daha önce bağlandığı Wi-Fi ağlarının adlarını gösterir.", False),
    "wifi_adapters": ("📶 Wi-Fi kartı bilgisi",
        "Wi-Fi kartının durumunu ve bağlantı hızını gösterir.", False),
    "ipconfig": ("🌐 IP ve DNS bilgileri",
        "Bilgisayarın IP adresini, ağ geçidini ve DNS sunucularını gösterir.", False),
    "network_test": ("🧪 İnternet bağlantı testi",
        "İnternete ulaşılıyor mu ve alan adları çözülüyor mu diye test eder.", False),
    "ping_host": ("📶 Ping at (bir adrese ulaş)",
        "Yazdığınız adresin cevap verip vermediğini ve ne kadar sürede verdiğini ölçer.", False),
    "tracert_host": ("🧭 Yol izle (Traceroute)",
        "Bir adrese giden yolu adım adım gösterir; bağlantının nerede koptuğunu bulur.", False),
    "nslookup_host": ("🔤 Alan adı sorgula (DNS)",
        "Bir internet adresinin hangi IP'ye karşılık geldiğini sorgular.", False),
    "route": ("🗺 Yönlendirme tablosu",
        "Ağ trafiğinin hangi yoldan çıkacağını gösteren tabloyu listeler.", False),
    "open_ports": ("🚪 Açık ağ portları",
        "Hangi programın ağdan bağlantı beklediğini listeler. Şüpheli programları yakalamaya yarar.", False),
    "flush_dns": ("♻ DNS önbelleğini temizle",
        "Bir site açılmıyor ama başkasında açılıyorsa eski kayıtları siler. Risksizdir.", False),
    "winsock_reset": ("♻ Ağ katmanını sıfırla (Winsock)",
        "İnternet bağlantı sorunlarında ağ yapısını fabrika ayarına döndürür. Yeniden başlatma gerekir.", True),
    "ip_reset": ("♻ IP ayarlarını sıfırla",
        "Bozuk IP yapılandırmasını temizler. Sabit IP ayarlarınız silinir; yeniden başlatma gerekir.", True),
    "network_ui": ("⚙ Ağ ayarlarını aç",
        "Windows'un Ağ ve İnternet ayarlarını açar.", False),
    "ncpa": ("🔌 Ağ bağlantıları penceresi",
        "Ethernet ve Wi-Fi adaptörlerini etkinleştirmek veya IP vermek için klasik ağ penceresini açar.", False),
    "net_adapters": ("🧩 Ağ adaptörlerini listele",
        "Tüm ağ kartlarının durumunu, hızını ve MAC adresini gösterir.", False),
    "network_report": ("📄 Ağ raporu oluştur",
        "Tüm ağ bilgilerini tek bir metin dosyasına yazıp masaüstüne kaydeder.", False),
    # --- Sistem ---
    "compmgmt": ("🖥 Bilgisayar Yönetimi", "Disk, kullanıcı, hizmet ve olay kayıtlarını tek yerde toplayan konsolu açar.", False),
    "services": ("⚙ Hizmetler", "Arka planda çalışan Windows hizmetlerini başlatır, durdurur veya ayarlar.", False),
    "taskschd": ("📅 Görev Zamanlayıcı", "Belirli zamanlarda otomatik çalışan görevleri gösterir ve yönetir.", False),
    "eventvwr": ("📋 Olay Görüntüleyici", "Windows'un tuttuğu hata ve uyarı kayıtlarını açar.", False),
    "devmgmt": ("🧩 Aygıt Yöneticisi", "Donanımları ve sürücüleri gösterir; sorunlu cihazlar sarı işaretle görünür.", False),
    "msinfo": ("🧠 Sistem Bilgisi", "Donanım, sürücü ve yazılım ortamının ayrıntılı dökümünü açar.", False),
    "dxdiag": ("📊 DirectX Tanılama", "Ekran kartı, ses ve DirectX bilgilerini gösterir.", False),
    "winver": ("📄 Windows sürümü", "Kurulu Windows sürümünü ve sürüm numarasını gösterir.", False),
    "appwiz": ("📦 Programlar ve Özellikler", "Kurulu programları kaldırmak veya onarmak için klasik pencereyi açar.", False),
    "msconfig": ("🛠 Sistem Yapılandırması", "Güvenli mod ve önyükleme ayarlarını açar.", False),
    "sysdm": ("🏷 Sistem Özellikleri", "Bilgisayar adı, uzak masaüstü ve sistem koruma ayarlarını açar.", False),
    "regedit": ("🧬 Kayıt Defteri Düzenleyicisi", "Windows'un gelişmiş ayar veritabanını açar. Yalnızca ne yaptığınızı biliyorsanız kullanın.", False),
    "powershell": ("⌨ PowerShell", "Gelişmiş komut satırını (yönetici yetkisiyle) açar.", False),
    "cmd": ("⌨ Komut İstemi (CMD)", "Klasik komut satırını (yönetici yetkisiyle) açar.", False),
    "system_report": ("📄 Tam sistem raporu", "İşlemci, RAM, disk ve ağ bilgilerini tek dosyada toplayıp masaüstüne kaydeder.", False),
    "windows_info": ("🖥 Bilgisayar kimlik kartı", "Marka, model, seri no, BIOS, Windows, işlemci ve ekran kartı bilgisini özetler.", False),
    # --- Yerleşik IT araçları ---
    "startup_apps": ("🚀 Açılışta çalışan programlar", "Windows ile birlikte başlayan programların listesi. Fazlası açılışı yavaşlatır.", False),
    "installed_apps": ("📚 Kurulu programlar listesi", "Bilgisayardaki tüm programları sürümüyle listeler; envanter çıkarmak için idealdir.", False),
    "installed_updates": ("🧾 Yüklü Windows güncellemeleri", "Son yüklenen 30 güncellemeyi tarihleriyle gösterir.", False),
    "stopped_services": ("🛑 Çalışması gerekip durmuş hizmetler", "Otomatik başlaması gereken ama çalışmayan hizmetleri bulur.", False),
    "event_errors": ("🚨 Son 3 günün hataları", "Sistem ve uygulama kayıtlarındaki kritik hataları ve hata düzeyindeki olayları listeler.", False),
    "minidumps": ("💥 Mavi ekran (BSOD) kayıtları", "Bilgisayar mavi ekranla çöktüyse bıraktığı kayıt dosyalarını listeler.", False),
    "hosts_file": ("📝 Hosts dosyasını göster", "Sitelerin yönlendirmesini değiştiren dosyayı gösterir. Zararlılar burayı değiştirir.", False),
    # --- Resmi web siteleri ---
    "url_sysinternals": ("🧰 Sysinternals Suite", "Microsoft'un profesyonel tanılama araç seti (Process Explorer, Autoruns vb.).", False),
    "url_autoruns": ("🚀 Autoruns", "Açılışta çalışan HER ŞEYİ gösterir; gizli zararlıları bulmak için kullanılır.", False),
    "url_procexp": ("🔬 Process Explorer", "Gelişmiş Görev Yöneticisi; hangi işlem neyi açmış, kim başlatmış görürsünüz.", False),
    "url_hwinfo": ("🧠 HWiNFO", "Tüm donanımın ve sensörlerin (ısı, voltaj, hız) ayrıntılı bilgisini verir.", False),
    "url_cpuz": ("🧰 CPU-Z", "İşlemci, anakart ve RAM'in tam özelliklerini gösterir.", False),
    "url_gpuz": ("🎮 GPU-Z", "Ekran kartının modelini, hızını ve sıcaklığını gösterir.", False),
    "url_crystaldisk": ("💽 CrystalDiskInfo", "Diskin sağlığını ve ısısını renkli göstergeyle verir.", False),
    "url_crystalmark": ("🏎 CrystalDiskMark", "Diskin okuma/yazma hızını ölçer.", False),
    "url_wiztree": ("🗂 WizTree", "Diski saniyeler içinde tarar, en büyük dosyaları görsel haritayla gösterir.", False),
    "url_everything": ("📁 Everything", "Bilgisayardaki herhangi bir dosyayı anında bulan arama aracı.", False),
    "url_memtest": ("🧬 MemTest86", "RAM'i USB'den başlatarak derinlemesine test eder.", False),
    "url_occt": ("🔥 OCCT", "İşlemci, ekran kartı ve güç kaynağına stres testi uygular; kararlılığı ölçer.", False),
    "url_ddu": ("🧹 Display Driver Uninstaller", "Ekran kartı sürücüsünü kalıntısız siler; temiz kurulum öncesi kullanılır.", False),
    "url_wireshark": ("🦈 Wireshark", "Ağ trafiğini paket paket inceleyen standart analiz aracı.", False),
    "url_nmap": ("🛰 Nmap", "Ağdaki cihazları ve açık portları tarar; güvenlik denetimi için kullanılır.", False),
    "url_angryip": ("🔎 Angry IP Scanner", "Ağdaki tüm cihazları hızlıca bulup listeler.", False),
    "url_putty": ("🖧 PuTTY", "Sunucu ve ağ cihazlarına SSH/Telnet ile bağlanma aracı.", False),
    "url_rufus": ("💾 Rufus", "Windows kurulum USB'si hazırlar.", False),
    "url_ventoy": ("💾 Ventoy", "Bir USB'ye birden fazla ISO atıp istediğinizi başlatmanızı sağlar.", False),
    "url_windows": ("🪟 Microsoft Windows indir", "Windows 11 kurulum medyasını resmi Microsoft sayfasından indirirsiniz.", False),
    "url_brand_drivers": ("🏷 Marka sürücü sayfası", "Bilgisayarınızın üreticisinin resmi sürücü/destek sayfasını açar.", False),
    "url_nvidia": ("🟩 NVIDIA sürücüleri", "NVIDIA ekran kartı için resmi sürücü sayfası.", False),
    "url_amd": ("🟥 AMD sürücüleri", "AMD ekran kartı/işlemci için resmi sürücü sayfası.", False),
    "url_intel": ("🟦 Intel sürücü asistanı", "Intel bileşenlerinin sürücülerini otomatik algılayan resmi sayfa.", False),
    "url_powertoys": ("🛠 PowerToys", "Microsoft'un Windows'u güçlendiren yardımcı araç seti.", False),
    "url_7zip": ("📦 7-Zip", "ZIP, RAR, 7z dosyalarını açan ücretsiz arşiv aracı.", False),
    "url_notepadpp": ("📝 Notepad++", "Yapılandırma ve günlük dosyaları için hızlı metin düzenleyici.", False),
    "url_malwarebytes": ("🦠 Malwarebytes", "Antivirüsün kaçırdığı zararlıları bulan ikinci görüş tarayıcısı.", False),
    "url_ninite": ("📋 Ninite", "Sık kullanılan programları tek seferde toplu kurma servisi.", False),
}

URLS = {
    "url_sysinternals": "https://learn.microsoft.com/sysinternals/downloads/sysinternals-suite",
    "url_autoruns": "https://learn.microsoft.com/sysinternals/downloads/autoruns",
    "url_procexp": "https://learn.microsoft.com/sysinternals/downloads/process-explorer",
    "url_hwinfo": "https://www.hwinfo.com/download/",
    "url_cpuz": "https://www.cpuid.com/softwares/cpu-z.html",
    "url_gpuz": "https://www.techpowerup.com/gpuz/",
    "url_crystaldisk": "https://crystalmark.info/en/software/crystaldiskinfo/",
    "url_crystalmark": "https://crystalmark.info/en/software/crystaldiskmark/",
    "url_wiztree": "https://diskanalyzer.com/",
    "url_everything": "https://www.voidtools.com/",
    "url_memtest": "https://www.memtest86.com/",
    "url_occt": "https://www.ocbase.com/",
    "url_ddu": "https://www.wagnardsoft.com/",
    "url_wireshark": "https://www.wireshark.org/download.html",
    "url_nmap": "https://nmap.org/download.html",
    "url_angryip": "https://angryip.org/download/",
    "url_putty": "https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html",
    "url_rufus": "https://rufus.ie/",
    "url_ventoy": "https://www.ventoy.net/",
    "url_windows": "https://www.microsoft.com/software-download/windows11",
    "url_nvidia": "https://www.nvidia.com/Download/index.aspx",
    "url_amd": "https://www.amd.com/en/support",
    "url_intel": "https://www.intel.com/content/www/us/en/support/detect.html",
    "url_powertoys": "https://learn.microsoft.com/windows/powertoys/",
    "url_7zip": "https://www.7-zip.org/",
    "url_notepadpp": "https://notepad-plus-plus.org/downloads/",
    "url_malwarebytes": "https://www.malwarebytes.com/mwb-download",
    "url_ninite": "https://ninite.com/",
}

BRAND_URLS = {
    "dell": "https://www.dell.com/support/home/",
    "hp": "https://support.hp.com/drivers",
    "hewlett": "https://support.hp.com/drivers",
    "lenovo": "https://support.lenovo.com/",
    "asus": "https://www.asus.com/support/",
    "msi": "https://www.msi.com/support",
    "micro-star": "https://www.msi.com/support",
    "acer": "https://www.acer.com/support",
    "samsung": "https://www.samsung.com/support/",
    "toshiba": "https://support.dynabook.com/",
    "dynabook": "https://support.dynabook.com/",
    "gigabyte": "https://www.gigabyte.com/Support",
    "huawei": "https://consumer.huawei.com/en/support/",
    "casper": "https://www.casper.com.tr/destek",
    "monster": "https://www.monsternotebook.com.tr/destek",
}

# Sistem pencerelerini doğrudan açan eylemler
OPENERS = {
    "restore_ui": "rstrui.exe", "windows_update": "ms-settings:windowsupdate",
    "cleanmgr": "cleanmgr.exe", "wsreset": "wsreset.exe",
    "defender_ui": "windowsdefender:", "mrt": "mrt.exe", "firewall": "wf.msc",
    "lusrmgr": "lusrmgr.msc", "diskmgmt": "diskmgmt.msc", "dfrgui": "dfrgui.exe",
    "explorer_c": "C:\\", "power_ui": "powercfg.cpl", "taskmgr": "taskmgr.exe",
    "perfmon": "perfmon.exe", "resmon": "resmon.exe", "gamebar": "ms-settings:gaming-gamebar",
    "network_ui": "ms-settings:network", "ncpa": "ncpa.cpl", "compmgmt": "compmgmt.msc",
    "services": "services.msc", "taskschd": "taskschd.msc", "eventvwr": "eventvwr.msc",
    "devmgmt": "devmgmt.msc", "msinfo": "msinfo32.exe", "dxdiag": "dxdiag.exe",
    "winver": "winver.exe", "appwiz": "appwiz.cpl", "msconfig": "msconfig.exe",
    "sysdm": "sysdm.cpl", "regedit": "regedit.exe", "powershell": "powershell.exe",
    "cmd": "cmd.exe", "ram_test": "mdsched.exe", "startup_ui": "ms-settings:startupapps",
}

# Kullanıcıdan adres isteyen eylemler: id -> (soru, varsayılan)
PROMPT_ACTIONS = {
    "ping_host": ("Hangi adrese ping atılsın?\n(örnek: 8.8.8.8 veya google.com)", "8.8.8.8"),
    "tracert_host": ("Hangi adrese giden yol izlensin?\n(örnek: google.com)", "google.com"),
    "nslookup_host": ("Hangi alan adı sorgulansın?\n(örnek: www.microsoft.com)", "www.microsoft.com"),
}

# Kategori sayfaları: (kenar çubuğu simgesi, ad, başlık, alt başlık, [kartlar])
CATEGORIES = [
    ("▣", "Kontrol Merkezi", "Kontrol Merkezi",
     "Bilgisayarınızın canlı durumunu izleyin ve en sık kullanılan işlemlere buradan ulaşın.", [
        ("⚡ Hızlı Bakım", "Her gün güvenle kullanılabilecek işlemler.", "green",
         ["health_check", "cleanup", "sfc"]),
        ("🛡 Güvenlik", "Virüs koruması ve zararlı yazılım kontrolü.", "red",
         ["defender_update", "defender_quick", "mrt"]),
        ("🌐 Ağ", "İnternet sorunlarını bulun.", "blue",
         ["network_test", "ipconfig", "flush_dns"]),
        ("🧰 Hızlı Erişim", "Sık kullanılan yönetim araçları.", "purple",
         ["taskmgr", "devmgmt", "top_processes"])]),
    ("🛡", "Güvenlik", "Güvenlik & Virüs Temizliği",
     "Virüs koruması, güvenlik duvarı, hesaplar ve şifreleme durumunu kontrol edin.", [
        ("Microsoft Defender", "Windows'un yerleşik antivirüsü.", "red",
         ["defender_update", "defender_quick", "defender_full", "defender_status"]),
        ("Zararlı Yazılım Temizleme", "Microsoft'un ek temizleme aracı.", "cyan",
         ["mrt", "mrt_about", "defender_ui"]),
        ("Ağ ve Hesap Güvenliği", "Dışarıdan erişim ve hesap kontrolü.", "green",
         ["firewall_status", "firewall", "local_users_list", "shares"]),
        ("Veri ve Lisans", "Şifreleme ve lisans doğrulama.", "purple",
         ["bitlocker", "activation", "lusrmgr"])]),
    ("⚙", "Bakım & Onarım", "Bakım & Onarım",
     "Windows'u onarın, temizleyin ve sorun çıkmadan önce yedek noktası alın.", [
        ("Sistem Onarımı", "Bozuk Windows dosyalarını düzeltir.", "cyan",
         ["sfc", "dism", "dism_check"]),
        ("Yedek ve Geri Dönüş", "Değişiklik öncesi güvenlik ağı.", "purple",
         ["restore_point", "restore_ui"]),
        ("Windows Update", "Güncelleme sorunlarını çözün.", "green",
         ["windows_update", "update_reset", "installed_updates"]),
        ("Temizlik", "Gereksiz dosyalardan kurtulun.", "yellow",
         ["cleanup", "cleanup_windows", "cleanmgr", "wsreset"])]),
    ("◈", "Disk & USB", "Disk, SSD & USB",
     "Disk sağlığını, boş alanı ve dosya sistemi hatalarını kontrol edin.", [
        ("Disk Sağlığı", "Diskiniz ölmeden önce uyarı alın.", "purple",
         ["disk_ps", "smart_health", "disk_info"]),
        ("Alan Yönetimi", "Disk neden doldu?", "yellow",
         ["drive_space", "big_folders", "cleanmgr"]),
        ("Optimizasyon", "Diski hızlı tutun.", "green",
         ["optimize_c", "dfrgui", "diskmgmt"]),
        ("Dosya Sistemi", "Disk hatalarını bulun ve onarın.", "red",
         ["chkdsk_scan", "chkdsk_fix", "diskpart_info"]),
        ("Sürücüler (Driver)", "Cihaz sürücülerini inceleyin.", "cyan",
         ["drivers", "devmgmt", "explorer_c"])]),
    ("⚡", "Performans", "Performans & Hız",
     "Bilgisayar neden yavaş? Nedenini bulun ve hızlandırın.", [
        ("Yavaşlık Teşhisi", "Kaynakları en çok kim yiyor?", "green",
         ["top_processes", "taskmgr", "resmon", "perfmon"]),
        ("Açılış Hızı", "Windows'un geç açılmasını düzeltin.", "yellow",
         ["startup_apps", "startup_ui", "stopped_services"]),
        ("Güç Yönetimi", "Hız ve pil dengesi.", "cyan",
         ["ultimate_performance", "power_plans", "power_ui"]),
        ("Bellek (RAM)", "RAM miktarı ve hata testi.", "purple",
         ["ram_info", "ram_test"]),
        ("Oyun", "Oyun performansı ayarları.", "blue",
         ["game_mode", "gamebar", "winsat"]),
        ("Dizüstü / Pil", "Pil ömrü raporları.", "red",
         ["battery_report", "energy_report"])]),
    ("⌁", "Ağ & Wi-Fi", "Ağ & Wi-Fi",
     "İnternet bağlantı sorunlarını bulun, test edin ve onarın.", [
        ("Bağlantı Testi", "İnternet var mı, nerede kopuyor?", "blue",
         ["network_test", "ping_host", "tracert_host", "nslookup_host"]),
        ("Ağ Bilgileri", "IP, DNS ve adaptörler.", "cyan",
         ["ipconfig", "net_adapters", "route", "open_ports"]),
        ("Wi-Fi", "Kablosuz ağ araçları.", "green",
         ["wifi_scan", "wifi_profiles", "wifi_adapters"]),
        ("Onarım", "Bağlantı sorunlarını giderin.", "red",
         ["flush_dns", "winsock_reset", "ip_reset"]),
        ("Ayarlar ve Rapor", "Ayarlara ve rapora ulaşın.", "purple",
         ["network_ui", "ncpa", "network_report"])]),
    ("▤", "Sistem Araçları", "Sistem Araçları",
     "Windows yönetim konsolları, donanım bilgisi ve raporlama.", [
        ("Yönetim Konsolları", "Profesyonel yönetim araçları.", "cyan",
         ["compmgmt", "services", "taskschd", "eventvwr"]),
        ("Donanım Bilgisi", "Cihazınız tam olarak nedir?", "green",
         ["windows_info", "msinfo", "dxdiag", "devmgmt"]),
        ("Programlar ve Ayarlar", "Kurulum ve sistem ayarları.", "yellow",
         ["appwiz", "msconfig", "sysdm", "regedit"]),
        ("Raporlama", "Masaüstüne rapor üretir.", "purple",
         ["system_report", "network_report", "winver"]),
        ("Komut Satırı", "Gelişmiş kullanıcılar için.", "red",
         ["powershell", "cmd"])]),
    ("🧪", "Yerleşik IT Araçları", "Yerleşik IT Teşhis Araçları",
     "Profesyonel IT desteğinin ilk baktığı yerler; tek tıkla, sade çıktıyla.", [
        ("Envanter", "Bilgisayarda ne var?", "cyan",
         ["windows_info", "installed_apps", "installed_updates", "drivers"]),
        ("Hata Avcılığı", "Sorunun izini sürün.", "red",
         ["event_errors", "minidumps", "stopped_services"]),
        ("Güvenlik Denetimi", "Şüpheli bir şey var mı?", "yellow",
         ["open_ports", "startup_apps", "hosts_file", "shares"]),
        ("Donanım Sağlığı", "Disk ve sürücü kontrolü.", "green",
         ["smart_health", "disk_ps", "drive_space", "ram_test"])]),
    ("◆", "IT Programları", "Profesyonel IT Programları",
     "Sadece resmi üretici sitelerini açar; hiçbir şey sessizce kurulmaz.", [
        ("Microsoft Sysinternals", "IT dünyasının vazgeçilmez seti.", "cyan",
         ["url_sysinternals", "url_autoruns", "url_procexp"]),
        ("Donanım Analizi", "Donanım özellikleri ve sensörler.", "green",
         ["url_hwinfo", "url_cpuz", "url_gpuz"]),
        ("Disk & Depolama", "Disk sağlığı, hız ve alan.", "purple",
         ["url_crystaldisk", "url_crystalmark", "url_wiztree", "url_everything"]),
        ("Test & Stres", "Kararlılığı ölçün.", "red",
         ["url_memtest", "url_occt", "url_ddu"]),
        ("Ağ Araçları", "Ağ analizi ve bağlantı.", "blue",
         ["url_wireshark", "url_nmap", "url_angryip", "url_putty"]),
        ("USB & Kurulum", "Windows kurulum medyası.", "yellow",
         ["url_rufus", "url_ventoy", "url_windows"]),
        ("Sürücü Sayfaları", "Resmi üretici sürücüleri.", "cyan",
         ["url_brand_drivers", "url_nvidia", "url_amd", "url_intel"]),
        ("Günlük Yardımcılar", "Her teknisyenin masaüstünde olur.", "green",
         ["url_powertoys", "url_7zip", "url_notepadpp", "url_malwarebytes", "url_ninite"])]),
]

# --------------------------------------------------------------------------
#  WINDOWS YARDIMCILARI
# --------------------------------------------------------------------------
OEM_ENC = "utf-8"
try:
    OEM_ENC = f"cp{ctypes.windll.kernel32.GetOEMCP()}"
except Exception:
    pass


def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def elevate_to_admin():
    """Yönetici yetkisiyle yeniden başlatır. Reddedilirse False döner (kullanıcı modu)."""
    if os.name != "nt" or is_admin():
        return True
    try:
        if getattr(sys, "frozen", False):
            exe, params = sys.executable, subprocess.list2cmdline(sys.argv[1:])
        else:
            exe = sys.executable
            params = subprocess.list2cmdline([os.path.abspath(sys.argv[0])] + sys.argv[1:])
        ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params,
                                                  os.getcwd(), 1)
        if int(ret) > 32:
            sys.exit(0)
    except SystemExit:
        raise
    except Exception:
        pass
    return False


def ps(command, timeout=900):
    return subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
         "[Console]::OutputEncoding=[Text.Encoding]::UTF8;" + command],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout, creationflags=CREATE_NO_WINDOW)


def psout(command, timeout=900, empty="İşlem tamamlandı (gösterilecek çıktı yok)."):
    r = ps(command, timeout)
    out = (r.stdout or "").strip()
    err = (r.stderr or "").strip()
    if err and not out:
        out = err
    elif err:
        out += "\n\n[Uyarı]\n" + err
    return out or empty


def run_cmd(command, timeout=300, input_text=None):
    return subprocess.run(
        command, capture_output=True, text=True, encoding=OEM_ENC,
        errors="replace", timeout=timeout, input=input_text,
        creationflags=CREATE_NO_WINDOW)


def cmd_out(command, timeout=300, input_text=None):
    r = run_cmd(command, timeout, input_text)
    out = (r.stdout or "").strip()
    err = (r.stderr or "").strip()
    text = out + (f"\n\n{err}" if err else "")
    return text or f"Komut tamamlandı. Çıkış kodu: {r.returncode}"


def get_system_info():
    brand, model = "Bilinmiyor", "Bilinmiyor"
    try:
        r = ps("$c=Get-CimInstance Win32_ComputerSystem;$c.Manufacturer;$c.Model", 30)
        lines = [l.strip() for l in r.stdout.splitlines() if l.strip()]
        if len(lines) >= 1:
            brand = lines[0]
        if len(lines) >= 2:
            model = lines[1]
    except Exception:
        pass
    return brand, model


def open_url(url):
    try:
        webbrowser.open(url)
    except Exception as exc:
        messagebox.showerror("Tarayıcı Hatası", str(exc))


# ---- Hızlı canlı ölçümler (PowerShell'siz, ctypes ile) ----
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]


class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", ctypes.c_uint32), ("dwHighDateTime", ctypes.c_uint32)]


class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [("ACLineStatus", ctypes.c_ubyte), ("BatteryFlag", ctypes.c_ubyte),
                ("BatteryLifePercent", ctypes.c_ubyte), ("SystemStatusFlag", ctypes.c_ubyte),
                ("BatteryLifeTime", ctypes.c_uint32), ("BatteryFullLifeTime", ctypes.c_uint32)]


_cpu_prev = [None]


def cpu_percent():
    idle, kern, user = FILETIME(), FILETIME(), FILETIME()
    ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kern), ctypes.byref(user))

    def val(t):
        return (t.dwHighDateTime << 32) | t.dwLowDateTime
    i, k, u = val(idle), val(kern), val(user)
    prev, _cpu_prev[0] = _cpu_prev[0], (i, k, u)
    if not prev:
        return 0.0
    di, dk, du = i - prev[0], k - prev[1], u - prev[2]
    total = dk + du
    if total <= 0:
        return 0.0
    return max(0.0, min(100.0, (total - di) * 100.0 / total))


def memory_status():
    m = MEMORYSTATUSEX()
    m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    total = m.ullTotalPhys / 1024 ** 3
    used = (m.ullTotalPhys - m.ullAvailPhys) / 1024 ** 3
    return float(m.dwMemoryLoad), used, total


def uptime_seconds():
    f = ctypes.windll.kernel32.GetTickCount64
    f.restype = ctypes.c_ulonglong
    return int(f() // 1000)


def battery_status():
    s = SYSTEM_POWER_STATUS()
    ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(s))
    if s.BatteryFlag == 128 or s.BatteryLifePercent == 255:
        return None
    return int(s.BatteryLifePercent), s.ACLineStatus == 1


def fmt_uptime(sec):
    d, rem = divmod(sec, 86400)
    h, rem = divmod(rem, 3600)
    return f"{d}g {h}sa {rem // 60}dk"


# --------------------------------------------------------------------------
#  GÖSTERGE (GAUGE) BİLEŞENLERİ
# --------------------------------------------------------------------------
class Gauge:
    """Tuval üzerine çizilen animasyonlu yarım-daire/ibreli gösterge."""

    def __init__(self, title, color, invert=False):
        self.title, self.color, self.invert = title, color, invert
        self.value = 0.0
        self.target = 0.0
        self.text = "—"
        self.sub = ""
        self.ids = {}

    def level_color(self, v):
        if self.invert:
            return RED if v < 20 else YELLOW if v < 40 else self.color
        return RED if v >= 85 else YELLOW if v >= 65 else self.color

    def set(self, target, text, sub=""):
        self.target, self.text, self.sub = max(0.0, min(100.0, target)), text, sub

    def draw(self, cv, cx, cy, r):
        self.cx, self.cy, self.r = cx, cy, r
        w = max(8, int(r * 0.14))
        box = (cx - r, cy - r, cx + r, cy + r)
        cv.create_oval(cx - r - w - 18, cy - r - w - 18, cx + r + w + 18, cy + r + w + 18,
                       outline="#0F1A2E", width=1)
        cv.create_arc(*box, start=225, extent=-270, style="arc", width=w, outline=TRACK)
        for i in range(11):
            a = math.radians(225 - 27 * i)
            r1 = r + w / 2 + 4
            r2 = r1 + (9 if i % 5 == 0 else 5)
            cv.create_line(cx + r1 * math.cos(a), cy - r1 * math.sin(a),
                           cx + r2 * math.cos(a), cy - r2 * math.sin(a),
                           fill=MUTED if i % 5 == 0 else "#33476B",
                           width=2 if i % 5 == 0 else 1)
        self.ids["arc"] = cv.create_arc(*box, start=225, extent=-0.01, style="arc",
                                        width=w, outline=self.color)
        self.ids["needle"] = cv.create_line(cx, cy, cx, cy, fill=WHITE, width=3, capstyle="round")
        cv.create_oval(cx - 7, cy - 7, cx + 7, cy + 7, fill=CARD, outline=self.color, width=2)
        self.ids["text"] = cv.create_text(cx, cy + r * 0.50, text=self.text, fill=WHITE,
                                          font=("Segoe UI", max(11, int(r * 0.24)), "bold"))
        cv.create_text(cx, cy + r * 0.84, text=self.title, fill=self.color,
                       font=("Segoe UI", 9, "bold"))
        self.ids["sub"] = cv.create_text(cx, cy + r * 1.02, text=self.sub, fill=MUTED,
                                         font=("Segoe UI", 8))
        self.apply(cv)

    def apply(self, cv):
        v = self.value
        a = math.radians(225 - 2.7 * v)
        length = self.r * 0.72
        cv.itemconfigure(self.ids["arc"], extent=-max(0.01, 2.7 * v), outline=self.level_color(v))
        cv.coords(self.ids["needle"], self.cx, self.cy,
                  self.cx + length * math.cos(a), self.cy - length * math.sin(a))
        cv.itemconfigure(self.ids["text"], text=self.text)
        cv.itemconfigure(self.ids["sub"], text=self.sub)

    def step(self, cv):
        d = self.target - self.value
        if abs(d) > 0.05:
            self.value += d * 0.22
        else:
            self.value = self.target
        self.apply(cv)


class GaugePanel:
    """Teknik ızgara arka planlı canlı gösterge paneli."""

    def __init__(self, parent, gauges, height=300):
        self.gauges = gauges
        self.canvas = tk.Canvas(parent, height=height, bg="#0A111F",
                                highlightthickness=1, highlightbackground=BORDER)
        self.canvas.bind("<Configure>", self._redraw)
        self._animate()

    def _redraw(self, event=None):
        cv = self.canvas
        w, h = cv.winfo_width(), cv.winfo_height()
        if w < 50:
            return
        cv.delete("all")
        for x in range(0, w, 32):
            cv.create_line(x, 0, x, h, fill=GRID)
        for y in range(0, h, 32):
            cv.create_line(0, y, w, y, fill=GRID)
        cv.create_text(16, 12, anchor="nw", text="● CANLI SİSTEM İZLEME", fill=CYAN,
                       font=("Segoe UI", 9, "bold"))
        cv.create_text(w - 16, 12, anchor="ne", text="Her saniye güncellenir", fill=MUTED,
                       font=("Segoe UI", 8))
        n = len(self.gauges)
        slot = w / n
        r = int(max(40, min(slot / 2 - 34, h / 2 - 52, 100)))
        cy = h / 2 + 8
        for i, g in enumerate(self.gauges):
            g.draw(cv, slot * (i + 0.5), cy, r)

    def _animate(self):
        try:
            if not self.canvas.winfo_exists():
                return
            if self.canvas.winfo_width() > 50:
                for g in self.gauges:
                    if g.ids:
                        g.step(self.canvas)
            self.canvas.after(40, self._animate)
        except tk.TclError:
            pass


# --------------------------------------------------------------------------
#  ANA UYGULAMA
# --------------------------------------------------------------------------
class ProITDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1280x820")
        self.root.minsize(1100, 720)
        self.root.configure(bg=BG)

        self.admin = is_admin()
        self.brand, self.model = "Yükleniyor…", ""
        self.event_queue = queue.Queue()
        self.busy = False
        self.log_lines = []
        self.gauge_panel = None
        self.gauges = {}
        self.info_vars = {}
        self.scroll_canvas = None
        self.sysdrive = os.environ.get("SystemDrive", "C:") + "\\"

        self._setup_style()
        self._build_ui()
        cpu_percent()  # ilk örneği al
        self._select_category(0)
        self._tick_metrics()
        self._poll_events()
        self.root.bind_all("<MouseWheel>", self._on_wheel)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        threading.Thread(target=self._load_brand, daemon=True).start()

    # ------------------------------ stil ---------------------------------
    def _setup_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Vertical.TScrollbar", background=BTN, troughcolor=BG,
                        bordercolor=BG, arrowcolor=CYAN, lightcolor=BTN, darkcolor=BTN)
        style.configure("Horizontal.TProgressbar", background=CYAN, troughcolor=PANEL,
                        bordercolor=PANEL, lightcolor=CYAN, darkcolor=CYAN)

    def _load_brand(self):
        brand, model = get_system_info()
        self.event_queue.put(("brand", brand, model))

    # ------------------------------ iskelet ------------------------------
    def _build_ui(self):
        side = tk.Frame(self.root, bg=SIDEBAR, width=275)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        top = tk.Frame(side, bg=SIDEBAR)
        top.pack(fill="x", padx=18, pady=(18, 8))
        tk.Label(top, text="⚡ aSiKuRT", font=("Segoe UI", 23, "bold"),
                 fg=CYAN, bg=SIDEBAR).pack(anchor="w")
        tk.Label(top, text="PRO IT CONTROL CENTER", font=("Segoe UI", 9, "bold"),
                 fg=MUTED, bg=SIDEBAR).pack(anchor="w")
        self.brand_label = tk.Label(top, text="Cihaz bilgisi okunuyor…", font=("Segoe UI", 8),
                                    fg="#B8C4D6", bg=SIDEBAR, wraplength=235, justify="left")
        self.brand_label.pack(anchor="w", pady=(4, 0))

        tk.Label(side, text="● YÖNETİCİ MODU" if self.admin else "⚠ KULLANICI MODU (sınırlı)",
                 font=("Segoe UI", 9, "bold"), fg=GREEN if self.admin else YELLOW,
                 bg="#132033", padx=12, pady=7).pack(fill="x", padx=18, pady=(4, 10))

        nav = tk.Frame(side, bg=SIDEBAR)
        nav.pack(fill="both", expand=True)
        self.nav_buttons = []
        for i, cat in enumerate(CATEGORIES):
            b = tk.Button(nav, text=f"  {cat[0]}   {cat[1]}", anchor="w", relief="flat", bd=0,
                          bg=SIDEBAR, fg="#C7D1DF", activebackground=HOVER,
                          activeforeground=CYAN, font=("Segoe UI", 10, "bold"),
                          padx=14, pady=9, cursor="hand2",
                          command=lambda x=i: self._select_category(x))
            b.pack(fill="x", padx=10, pady=1)
            b.bind("<Enter>", lambda e, b=b: b["bg"] != "#1C304A" and b.configure(bg=HOVER))
            b.bind("<Leave>", lambda e, b=b: b["bg"] != "#1C304A" and b.configure(bg=SIDEBAR))
            self.nav_buttons.append(b)

        tk.Label(side, text=f"v{APP_VERSION}  •  Windows IT Toolkit", font=("Segoe UI", 8),
                 fg="#59687E", bg=SIDEBAR).pack(side="bottom", pady=12)

        main = tk.Frame(self.root, bg=BG)
        main.pack(side="right", fill="both", expand=True)

        header = tk.Frame(main, bg=PANEL, height=68)
        header.pack(fill="x", padx=16, pady=(16, 10))
        header.pack_propagate(False)
        left = tk.Frame(header, bg=PANEL)
        left.pack(side="left", fill="y")
        tk.Label(left, text="IT OPERASYON MERKEZİ", font=("Segoe UI", 14, "bold"),
                 fg=WHITE, bg=PANEL).pack(anchor="w", padx=18, pady=(10, 0))
        self.header_sub = tk.Label(left, text="Sistem hazır", font=("Segoe UI", 8),
                                   fg=MUTED, bg=PANEL)
        self.header_sub.pack(anchor="w", padx=18)
        self.header_stats = tk.Label(header, text="CPU —    RAM —    DISK —",
                                     font=("Consolas", 10, "bold"), fg=CYAN, bg=PANEL)
        self.header_stats.pack(side="right", padx=20)

        self.content = tk.Frame(main, bg=BG)
        self.content.pack(fill="both", expand=True, padx=16)

        bottom = tk.Frame(main, bg=PANEL, height=46)
        bottom.pack(fill="x", padx=16, pady=(10, 16))
        bottom.pack_propagate(False)
        self.status = tk.Label(bottom, text="● HAZIR", font=("Segoe UI", 9, "bold"),
                               fg=GREEN, bg=PANEL)
        self.status.pack(side="left", padx=14)
        self.progress = ttk.Progressbar(bottom, mode="indeterminate", length=170)
        self.progress.pack(side="left", padx=10)
        tk.Button(bottom, text="Kapat", command=self._on_close, bg=RED, fg="white",
                  activebackground="#D93E58", relief="flat", padx=14,
                  cursor="hand2").pack(side="right", padx=10, pady=7)
        tk.Button(bottom, text="İşlem Günlüğü", command=self.show_log, bg=BTN, fg=CYAN,
                  activebackground=HOVER, relief="flat", padx=13,
                  cursor="hand2").pack(side="right", padx=5, pady=7)

    def _on_wheel(self, e):
        try:
            if e.widget.winfo_toplevel() is not self.root:
                return
            cv = self.scroll_canvas
            if cv and cv.winfo_exists() and cv.yview() != (0.0, 1.0):
                cv.yview_scroll(int(-e.delta / 120), "units")
        except Exception:
            pass

    def _clear(self):
        self.gauge_panel = None
        self.gauges = {}
        self.info_vars = {}
        for w in self.content.winfo_children():
            w.destroy()

    def _select_category(self, index):
        for i, b in enumerate(self.nav_buttons):
            b.configure(bg="#1C304A" if i == index else SIDEBAR,
                        fg=CYAN if i == index else "#C7D1DF")
        self._clear()
        cv = tk.Canvas(self.content, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(self.content, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        self.page = tk.Frame(cv, bg=BG)
        win = cv.create_window((0, 0), window=self.page, anchor="nw")
        self.page.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>", lambda e: cv.itemconfigure(win, width=e.width))
        self.scroll_canvas = cv

        _icon, _nav, title, subtitle, cards = CATEGORIES[index]
        f = tk.Frame(self.page, bg=BG)
        f.pack(fill="x", pady=(2, 10))
        tk.Label(f, text=title, font=("Segoe UI", 19, "bold"), fg=WHITE, bg=BG).pack(anchor="w")
        tk.Label(f, text=subtitle, font=("Segoe UI", 9), fg=MUTED, bg=BG).pack(anchor="w", pady=(2, 0))

        if index == 0:
            self._dashboard_top()
        self._cards(cards)

    # ------------------------------ kontrol merkezi ----------------------
    def _dashboard_top(self):
        self.gauges = {
            "cpu": Gauge("İŞLEMCİ", CYAN),
            "ram": Gauge("BELLEK (RAM)", GREEN),
            "disk": Gauge("DİSK (C:)", PURPLE),
            "pwr": Gauge("GÜÇ / PİL", YELLOW, invert=True),
        }
        self.gauge_panel = GaugePanel(self.page, list(self.gauges.values()), height=300)
        self.gauge_panel.canvas.pack(fill="x", pady=(0, 8))

        strip = tk.Frame(self.page, bg=BG)
        strip.pack(fill="x", pady=(0, 4))
        for c in range(4):
            strip.columnconfigure(c, weight=1)
        specs = [("ÇALIŞMA SÜRESİ", "uptime", YELLOW), ("BELLEK KULLANIMI", "mem", GREEN),
                 ("C: BOŞ ALAN", "free", PURPLE), ("KULLANICI", "user", CYAN)]
        for i, (label, key, color) in enumerate(specs):
            fr = tk.Frame(strip, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
            fr.grid(row=0, column=i, sticky="ew", padx=4)
            tk.Label(fr, text=label, font=("Segoe UI", 8, "bold"), fg=MUTED,
                     bg=CARD).pack(anchor="w", padx=12, pady=(8, 0))
            self.info_vars[key] = tk.StringVar(value="—")
            tk.Label(fr, textvariable=self.info_vars[key], font=("Segoe UI", 12, "bold"),
                     fg=color, bg=CARD).pack(anchor="w", padx=12, pady=(0, 8))

    # ------------------------------ kartlar ------------------------------
    def _cards(self, specs):
        holder = tk.Frame(self.page, bg=BG)
        holder.pack(fill="both", expand=True)
        holder.columnconfigure(0, weight=1, uniform="c")
        holder.columnconfigure(1, weight=1, uniform="c")
        for i, (title, subtitle, color, ids) in enumerate(specs):
            r, c = divmod(i, 2)
            col = COLORS.get(color, CYAN)
            f = tk.Frame(holder, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
            f.grid(row=r, column=c, sticky="nsew",
                   padx=(0, 6) if c == 0 else (6, 0), pady=6)
            tk.Frame(f, bg=col, width=4).pack(side="left", fill="y")
            body = tk.Frame(f, bg=CARD)
            body.pack(side="left", fill="both", expand=True, padx=14, pady=12)
            tk.Label(body, text=title, font=("Segoe UI", 11, "bold"), fg=WHITE,
                     bg=CARD).pack(anchor="w")
            tk.Label(body, text=subtitle, font=("Segoe UI", 8), fg=MUTED, bg=CARD,
                     wraplength=400, justify="left").pack(anchor="w", pady=(2, 0))
            for aid in ids:
                self._action_button(body, aid)

    def _action_button(self, parent, aid):
        label, desc, confirm = ACTIONS[aid]
        f = tk.Frame(parent, bg=BTN, cursor="hand2")
        f.pack(fill="x", pady=(8, 0))
        row = tk.Frame(f, bg=BTN)
        row.pack(fill="x", padx=12, pady=(8, 0))
        t = tk.Label(row, text=label, font=("Segoe UI", 10, "bold"), fg="#EAF2FF", bg=BTN, anchor="w")
        t.pack(side="left")
        badge = None
        if confirm:
            badge = tk.Label(row, text="ONAY İSTER", font=("Segoe UI", 7, "bold"),
                             fg=YELLOW, bg=BTN)
        elif aid.startswith("url_"):
            badge = tk.Label(row, text="↗ RESMİ SİTE", font=("Segoe UI", 7, "bold"),
                             fg=BLUE, bg=BTN)
        if badge:
            badge.pack(side="right")
        d = tk.Label(f, text=desc, font=("Segoe UI", 8), fg="#9FB0C8", bg=BTN,
                     wraplength=380, justify="left", anchor="w")
        d.pack(fill="x", padx=12, pady=(2, 9))

        widgets = [f, row, t, d] + ([badge] if badge else [])

        def paint(color):
            for w in widgets:
                w.configure(bg=color)
        for w in widgets:
            w.bind("<Enter>", lambda e: paint(HOVER))
            w.bind("<Leave>", lambda e: paint(BTN))
            w.bind("<Button-1>", lambda e, a=aid: self.request_action(a))

    # ------------------------------ aksiyon motoru -----------------------
    def request_action(self, action):
        label, desc, confirm = ACTIONS[action]

        if action.startswith("url_"):
            self._open_program_url(action)
            return
        if self.busy:
            messagebox.showwarning("Meşgul", "Başka bir işlem devam ediyor. Bitmesini bekleyin.")
            return

        param = None
        if action in PROMPT_ACTIONS:
            q, default = PROMPT_ACTIONS[action]
            param = simpledialog.askstring(label.split(" ", 1)[-1], q, initialvalue=default,
                                           parent=self.root)
            if not param:
                return
            param = param.strip()
            if not re.fullmatch(r"[A-Za-z0-9._:\-]{1,253}", param):
                messagebox.showerror("Geçersiz adres", "Yalnızca harf, rakam, nokta ve tire kullanın.")
                return

        if confirm:
            if not messagebox.askyesno(
                    "İşlemi Onayla",
                    f"{label}\n\n{desc}\n\nBu işlem sistem ayarlarını veya dosyalarını "
                    f"değiştirebilir.\nDevam edilsin mi?", icon="warning"):
                return

        self.busy = True
        self.progress.start(12)
        self.status.configure(text=f"● ÇALIŞIYOR: {label}", fg=YELLOW)
        self.header_sub.configure(text=f"İşlem yürütülüyor: {label}")
        threading.Thread(target=self._worker, args=(action, param), daemon=True).start()

    def _worker(self, action, param):
        try:
            self.event_queue.put(("ok", action, self.execute_action(action, param)))
        except subprocess.TimeoutExpired:
            self.event_queue.put(("ok", action,
                                  "⏱ İşlem çok uzun sürdüğü için durduruldu.\n"
                                  "Bilgisayar yoğun olabilir; biraz bekleyip tekrar deneyin."))
        except Exception:
            self.event_queue.put(("err", action, traceback.format_exc()))

    def _desktop(self):
        d = os.path.join(os.path.expanduser("~"), "Desktop")
        return d if os.path.isdir(d) else os.path.expanduser("~")

    def execute_action(self, a, param=None):
        label = ACTIONS[a][0]

        # --- Doğrudan pencere açanlar ---
        if a in OPENERS:
            os.startfile(OPENERS[a])
            return f"{label.split(' ', 1)[-1]} açıldı."

        # --- Temizlik ---
        if a == "cleanup":
            temp = os.environ.get("TEMP", "")
            count = freed = 0
            if temp and os.path.isdir(temp):
                for root, dirs, files in os.walk(temp, topdown=False):
                    for name in files:
                        p = os.path.join(root, name)
                        try:
                            size = os.path.getsize(p)
                            os.remove(p)
                            count += 1
                            freed += size
                        except OSError:
                            pass
                    for name in dirs:
                        try:
                            os.rmdir(os.path.join(root, name))
                        except OSError:
                            pass
            dns = cmd_out(["ipconfig", "/flushdns"])
            return (f"Temp temizliği tamamlandı.\nSilinen dosya: {count}\n"
                    f"Kazanılan alan: {freed / 1024 ** 2:.1f} MB\n\n{dns}")
        if a == "cleanup_windows":
            return psout(r'''$paths=@("$env:WINDIR\Temp","$env:LOCALAPPDATA\Temp");$n=0;$b=0;foreach($p in $paths){if(Test-Path $p){Get-ChildItem $p -Force -Recurse -ErrorAction SilentlyContinue|Where-Object{-not $_.PSIsContainer}|ForEach-Object{$l=$_.Length;try{Remove-Item $_.FullName -Force -ErrorAction Stop;$n++;$b+=$l}catch{}}}};"Temizlik tamamlandı. Silinen dosya: $n  Kazanılan alan: $([math]::Round($b/1MB,1)) MB"''')

        # --- Onarım ---
        if a == "sfc":
            return cmd_out(["sfc", "/scannow"], 3600)
        if a == "dism":
            return cmd_out(["DISM", "/Online", "/Cleanup-Image", "/RestoreHealth"], 3600)
        if a == "dism_check":
            return cmd_out(["DISM", "/Online", "/Cleanup-Image", "/CheckHealth"], 600)
        if a == "restore_point":
            return psout("Enable-ComputerRestore -Drive $env:SystemDrive;"
                         "Checkpoint-Computer -Description 'aSiKuRT_ProIT_Yedek' "
                         "-RestorePointType 'MODIFY_SETTINGS';"
                         "'Geri yükleme noktası oluşturuldu. (Windows 24 saatte en fazla 1 nokta alır.)'")
        if a == "update_reset":
            return psout(r'''Stop-Service wuauserv,bits,cryptsvc -Force -ErrorAction SilentlyContinue;Remove-Item "$env:WINDIR\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue;Start-Service cryptsvc,bits,wuauserv -ErrorAction SilentlyContinue;"Windows Update servisleri yenilendi. Şimdi Windows Update'ten güncellemeleri tekrar denetleyin."''')
        if a == "installed_updates":
            return psout("Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 30 "
                         "HotFixID,Description,InstalledOn | Format-Table -AutoSize | Out-String")

        # --- Güvenlik ---
        if a == "defender_update":
            return psout("Update-MpSignature; 'Virüs tanımları güncellendi.'")
        if a == "defender_quick":
            return psout("Start-MpScan -ScanType QuickScan; 'Hızlı tarama tamamlandı. Tehdit varsa Windows Güvenlik bildirir.'")
        if a == "defender_full":
            return psout("Start-MpScan -ScanType FullScan; 'Tam tarama tamamlandı. Tehdit varsa Windows Güvenlik bildirir.'", 14400)
        if a == "defender_status":
            return psout("Get-MpComputerStatus | Select-Object AntivirusEnabled,RealTimeProtectionEnabled,"
                         "AntivirusSignatureLastUpdated,AntivirusSignatureAge,QuickScanEndTime,FullScanEndTime "
                         "| Format-List | Out-String")
        if a == "mrt_about":
            return ("Microsoft Kötü Amaçlı Yazılımları Temizleme Aracı (MRT), yaygın zararlı "
                    "yazılımları arar ve siler. Aylık Windows Update ile güncellenir.\n\n"
                    "Kullanım: 'MRT'yi çalıştır' düğmesi → Hızlı tarama (önerilir) → İleri.\n"
                    "Antivirüsün yerine geçmez, tamamlayıcıdır.")
        if a == "firewall_status":
            return psout("Get-NetFirewallProfile | Select-Object Name,Enabled,DefaultInboundAction,"
                         "DefaultOutboundAction | Format-Table -AutoSize | Out-String")
        if a == "local_users_list":
            return psout("Get-LocalUser | Select-Object Name,Enabled,LastLogon,PasswordRequired "
                         "| Format-Table -AutoSize | Out-String")
        if a == "shares":
            return cmd_out(["net", "share"])
        if a == "bitlocker":
            return cmd_out(["manage-bde", "-status"])
        if a == "activation":
            slmgr = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "System32", "slmgr.vbs")
            return cmd_out(["cscript", "//nologo", slmgr, "/xpr"], 60)

        # --- Disk ---
        if a == "disk_info":
            return psout("Get-CimInstance Win32_DiskDrive | Select-Object Model,InterfaceType,MediaType,"
                         "@{N='Boyut_GB';E={[math]::Round($_.Size/1GB,1)}} | Format-Table -AutoSize | Out-String -Width 240")
        if a == "disk_ps":
            return psout("Get-PhysicalDisk | Select-Object FriendlyName,MediaType,HealthStatus,OperationalStatus,"
                         "@{N='Boyut_GB';E={[math]::Round($_.Size/1GB)}} | Format-Table -AutoSize | Out-String -Width 240;"
                         "'Not: HealthStatus = Healthy ise disk sağlıklıdır.'")
        if a == "drive_space":
            return psout("Get-Volume | Where-Object DriveLetter | Select-Object DriveLetter,FileSystemLabel,"
                         "FileSystem,HealthStatus,@{N='Boyut_GB';E={[math]::Round($_.Size/1GB,1)}},"
                         "@{N='Bos_GB';E={[math]::Round($_.SizeRemaining/1GB,1)}} | Format-Table -AutoSize | Out-String")
        if a == "smart_health":
            return psout("try{Get-PhysicalDisk | ForEach-Object{$d=$_;$c=$d | Get-StorageReliabilityCounter;"
                         "[pscustomobject]@{Disk=$d.FriendlyName;Saglik=$d.HealthStatus;Sicaklik_C=$c.Temperature;"
                         "Asinma_Yuzde=$c.Wear;Calisma_Saati=$c.PowerOnHours;Okuma_Hatasi=$c.ReadErrorsTotal;"
                         "Yazma_Hatasi=$c.WriteErrorsTotal}} | Format-List | Out-String}catch{'Bu disk için SMART verisi okunamadı.'}")
        if a == "big_folders":
            return psout(r'''Get-ChildItem $env:USERPROFILE -Directory -Force -ErrorAction SilentlyContinue | ForEach-Object { $s=(Get-ChildItem $_.FullName -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum; [pscustomobject]@{Klasor=$_.Name;Boyut_GB=[math]::Round($s/1GB,2)} } | Sort-Object Boyut_GB -Descending | Format-Table -AutoSize | Out-String''', 1200)
        if a == "optimize_c":
            return cmd_out(["defrag", "C:", "/O"], 3600)
        if a == "diskpart_info":
            return cmd_out(["diskpart.exe"], 60, input_text="list disk\nlist volume\nexit\n")
        if a == "drivers":
            return psout("Get-CimInstance Win32_PnPSignedDriver | Where-Object DeviceName | Select-Object "
                         "DeviceName,DriverVersion,Manufacturer | Sort-Object DeviceName | Format-Table -AutoSize "
                         "| Out-String -Width 240")
        if a == "chkdsk_scan":
            return cmd_out(["chkdsk", "C:", "/scan"], 3600)
        if a == "chkdsk_fix":
            return cmd_out(["chkdsk", "C:", "/f"], 3600, input_text="Y\n")

        # --- Performans ---
        if a == "ultimate_performance":
            one = cmd_out(["powercfg", "-duplicatescheme", "e9a42b02-d5df-448d-aa00-03f14749eb61"])
            m = re.search(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", one)
            msg = ""
            if m:
                msg = cmd_out(["powercfg", "/setactive", m.group(0)])
                msg = "Nihai Performans planı etkinleştirildi.\n" + (msg if "tamamlandı" not in msg else "")
            else:
                msg = "Bu bilgisayar Nihai Performans planını desteklemiyor olabilir.\n"
            return msg + "\n" + cmd_out(["powercfg", "/list"])
        if a == "power_plans":
            return cmd_out(["powercfg", "/list"])
        if a == "top_processes":
            return psout("Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 25 Name,Id,"
                         "@{N='RAM_MB';E={[math]::Round($_.WorkingSet64/1MB)}},"
                         "@{N='CPU_sn';E={[math]::Round($_.CPU,1)}} | Format-Table -AutoSize | Out-String")
        if a == "ram_info":
            return psout("Get-CimInstance Win32_PhysicalMemory | Select-Object BankLabel,Manufacturer,Speed,"
                         "@{N='Boyut_GB';E={[math]::Round($_.Capacity/1GB)}} | Format-Table -AutoSize | Out-String;"
                         "$c=Get-CimInstance Win32_ComputerSystem;"
                         "'Toplam RAM: ' + [math]::Round($c.TotalPhysicalMemory/1GB,2) + ' GB'")
        if a == "game_mode":
            import winreg
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar")
            winreg.SetValueEx(key, "AllowAutoGameMode", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "AutoGameModeEnabled", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            return "Oyun Modu etkinleştirildi."
        if a == "winsat":
            return cmd_out(["winsat", "formal"], 3600)
        if a == "battery_report":
            path = os.path.join(self._desktop(), "aSiKuRT_pil_raporu.html")
            return cmd_out(["powercfg", "/batteryreport", "/output", path]) + \
                "\n\nRapor masaüstüne kaydedildi; çift tıklayıp tarayıcıda açabilirsiniz."
        if a == "energy_report":
            path = os.path.join(self._desktop(), "aSiKuRT_enerji_raporu.html")
            return cmd_out(["powercfg", "/energy", "/output", path, "/duration", "60"], 300) + \
                "\n\nRapor masaüstüne kaydedildi."

        # --- Ağ ---
        if a == "wifi_scan":
            return cmd_out(["netsh", "wlan", "show", "networks", "mode=bssid"])
        if a == "wifi_profiles":
            return cmd_out(["netsh", "wlan", "show", "profiles"])
        if a == "wifi_adapters":
            return psout("Get-NetAdapter | Where-Object InterfaceDescription -match 'Wi-Fi|Wireless|802.11' | "
                         "Format-Table Name,Status,LinkSpeed,InterfaceDescription -AutoSize | Out-String -Width 240",
                         empty="Wi-Fi kartı bulunamadı.")
        if a == "ipconfig":
            return cmd_out(["ipconfig", "/all"])
        if a == "network_test":
            return (cmd_out(["ping", "1.1.1.1", "-n", "4"]) +
                    "\n\n--- DNS TESTİ ---\n" + cmd_out(["nslookup", "www.microsoft.com"]))
        if a == "ping_host":
            return cmd_out(["ping", param, "-n", "4"])
        if a == "tracert_host":
            return cmd_out(["tracert", "-d", "-h", "20", param], 300)
        if a == "nslookup_host":
            return cmd_out(["nslookup", param])
        if a == "route":
            return cmd_out(["route", "print"])
        if a == "open_ports":
            return psout("Get-NetTCPConnection -State Listen | Sort-Object LocalPort | Select-Object LocalAddress,"
                         "LocalPort,@{N='Program';E={(Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName}} "
                         "| Format-Table -AutoSize | Out-String")
        if a == "flush_dns":
            return cmd_out(["ipconfig", "/flushdns"])
        if a == "winsock_reset":
            return cmd_out(["netsh", "winsock", "reset"]) + "\n\nDeğişikliğin geçerli olması için bilgisayarı yeniden başlatın."
        if a == "ip_reset":
            return cmd_out(["netsh", "int", "ip", "reset"]) + "\n\nDeğişikliğin geçerli olması için bilgisayarı yeniden başlatın."
        if a == "net_adapters":
            return psout("Get-NetAdapter | Sort-Object Name | Format-Table Name,Status,LinkSpeed,MacAddress,"
                         "InterfaceDescription -AutoSize | Out-String -Width 260")
        if a == "network_report":
            path = os.path.join(self._desktop(), "aSiKuRT_ag_raporu.txt")
            content = [f"{APP_NAME} v{APP_VERSION}", "=" * 80,
                       "ADAPTÖRLER\n" + self.execute_action("net_adapters"),
                       "IPCONFIG /ALL\n" + self.execute_action("ipconfig"),
                       "ROUTE PRINT\n" + self.execute_action("route")]
            Path(path).write_text("\n\n".join(content), encoding="utf-8", errors="ignore")
            return f"Ağ raporu oluşturuldu:\n{path}"

        # --- Sistem ---
        if a == "system_report":
            path = os.path.join(self._desktop(), "aSiKuRT_sistem_raporu.txt")
            sections = [("KİMLİK KARTI", self.execute_action("windows_info")),
                        ("SYSTEMINFO", cmd_out(["systeminfo"], 180)),
                        ("RAM", self.execute_action("ram_info")),
                        ("DİSK SAĞLIĞI", self.execute_action("disk_ps")),
                        ("SÜRÜCÜLERDE ALAN", self.execute_action("drive_space")),
                        ("AĞ", self.execute_action("net_adapters"))]
            text = f"{APP_NAME} v{APP_VERSION}\n" + "=" * 90 + "\n"
            text += "\n\n".join(f"--- {n} ---\n{v}" for n, v in sections)
            Path(path).write_text(text, encoding="utf-8", errors="ignore")
            return f"Sistem raporu oluşturuldu:\n{path}"
        if a == "windows_info":
            return psout("$o=Get-CimInstance Win32_OperatingSystem;$b=Get-CimInstance Win32_BIOS;"
                         "$c=Get-CimInstance Win32_ComputerSystem;$p=Get-CimInstance Win32_Processor|Select-Object -First 1;"
                         "$g=Get-CimInstance Win32_VideoController|Select-Object -ExpandProperty Name;"
                         "[pscustomobject]@{Bilgisayar_Adi=$c.Name;Marka=$c.Manufacturer;Model=$c.Model;"
                         "Seri_No=$b.SerialNumber;BIOS=$b.SMBIOSBIOSVersion;Windows=$o.Caption;Surum=$o.Version;"
                         "Mimari=$o.OSArchitecture;Islemci=$p.Name;Ekran_Karti=($g -join ', ');"
                         "RAM_GB=[math]::Round($c.TotalPhysicalMemory/1GB,1);Windows_Kurulum=$o.InstallDate} "
                         "| Format-List | Out-String -Width 200")

        # --- Yerleşik IT araçları ---
        if a == "startup_apps":
            return psout("Get-CimInstance Win32_StartupCommand | Select-Object Name,Command,Location,User "
                         "| Format-List | Out-String -Width 250", empty="Açılışta çalışan program bulunamadı.")
        if a == "installed_apps":
            return psout(r'''$p='HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*','HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*';Get-ItemProperty $p -ErrorAction SilentlyContinue|Where-Object DisplayName|Sort-Object DisplayName -Unique|Select-Object DisplayName,DisplayVersion,Publisher|Format-Table -AutoSize|Out-String -Width 250''')
        if a == "stopped_services":
            return psout("Get-CimInstance Win32_Service | Where-Object {$_.StartMode -eq 'Auto' -and $_.State -ne 'Running'} "
                         "| Select-Object Name,DisplayName,State | Format-Table -AutoSize | Out-String -Width 250;"
                         "'Not: Bazı hizmetlerin (gecikmeli başlatma) durmuş görünmesi normaldir.'")
        if a == "event_errors":
            return psout(r'''$f=@{LogName='System','Application';Level=1,2;StartTime=(Get-Date).AddDays(-3)};Get-WinEvent -FilterHashtable $f -MaxEvents 40 -ErrorAction SilentlyContinue | Select-Object TimeCreated,LogName,ProviderName,Id,@{N='Mesaj';E={($_.Message -split "`n")[0]}} | Format-Table -Wrap -AutoSize | Out-String -Width 250''',
                         empty="Son 3 günde kritik hata bulunamadı. Bu iyi bir işaret.")
        if a == "minidumps":
            return psout(r'''Get-ChildItem "$env:WINDIR\Minidump" -ErrorAction SilentlyContinue | Select-Object Name,LastWriteTime,Length | Format-Table -AutoSize | Out-String''',
                         empty="Mavi ekran kaydı bulunamadı. Bu iyi bir işaret.")
        if a == "hosts_file":
            p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "System32", "drivers", "etc", "hosts")
            try:
                return Path(p).read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                return f"Hosts dosyası okunamadı: {exc}"

        if a == "health_check":
            return self.health_check()

        raise ValueError(f"Bilinmeyen işlem: {a}")

    # ------------------------------ sağlık kontrolü ----------------------
    def health_check(self):
        lines, warns = [], 0

        def add(ok, text):
            nonlocal warns
            if not ok:
                warns += 1
            lines.append(("✔  " if ok else "⚠  ") + text)

        du = shutil.disk_usage(self.sysdrive)
        free_pct = du.free / du.total * 100
        add(free_pct >= 15, f"Disk alanı: {self.sysdrive[:2]} sürücüsünde %{free_pct:.0f} boş "
                            f"({du.free / 1024 ** 3:.0f} GB)." +
            ("" if free_pct >= 15 else " Alan azalıyor; temizlik yapın."))
        load, used, total = memory_status()
        add(load < 85, f"Bellek: {used:.1f} / {total:.1f} GB kullanılıyor (%{load:.0f})." +
            ("" if load < 85 else " Bellek dolu; gereksiz programları kapatın."))
        days = uptime_seconds() / 86400
        add(days < 14, f"Çalışma süresi: {days:.1f} gün." +
            ("" if days < 14 else " Uzun süredir kapatılmadı; yeniden başlatmak iyi gelir."))

        script = r'''$r=[ordered]@{}
try{$m=Get-MpComputerStatus;$r.av=[bool]$m.AntivirusEnabled;$r.rt=[bool]$m.RealTimeProtectionEnabled;$r.sigAge=[int]$m.AntivirusSignatureAge}catch{}
try{$r.fw=@(Get-NetFirewallProfile|ForEach-Object{@{n="$($_.Name)";e=[bool]$_.Enabled}})}catch{}
try{$r.disks=@(Get-PhysicalDisk|ForEach-Object{@{n="$($_.FriendlyName)";h="$($_.HealthStatus)"}})}catch{}
try{$r.startup=@(Get-CimInstance Win32_StartupCommand).Count}catch{}
$r.reboot=[bool]((Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending') -or (Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired'))
try{$h=Get-HotFix|Where-Object InstalledOn|Sort-Object InstalledOn -Descending|Select-Object -First 1;if($h){$r.lastUpdate=$h.InstalledOn.ToString('yyyy-MM-dd')}}catch{}
$r|ConvertTo-Json -Depth 4 -Compress'''
        d = {}
        try:
            d = json.loads(ps(script, 300).stdout.strip() or "{}")
        except Exception:
            pass

        def as_list(x):
            return x if isinstance(x, list) else ([x] if x else [])

        if "av" in d:
            ok = d.get("av") and d.get("rt")
            add(bool(ok), "Virüs koruması: " + ("açık ve gerçek zamanlı çalışıyor." if ok
                                               else "KAPALI veya eksik. Windows Güvenlik'ten açın."))
            age = d.get("sigAge", 0)
            add(age <= 7, f"Virüs tanımları: {age} günlük." + ("" if age <= 7 else " Güncellemeniz önerilir."))
        else:
            add(False, "Virüs koruması okunamadı (başka bir antivirüs kullanılıyor olabilir).")
        fw = as_list(d.get("fw"))
        if fw:
            off = [x["n"] for x in fw if not x.get("e")]
            add(not off, "Güvenlik duvarı: " + ("tüm profillerde açık." if not off
                                               else "şu profillerde KAPALI: " + ", ".join(off)))
        disks = as_list(d.get("disks"))
        for dk in disks:
            ok = dk.get("h") == "Healthy"
            add(ok, f"Disk sağlığı ({dk.get('n')}): {dk.get('h')}." +
                ("" if ok else " Önemli verilerinizi hemen yedekleyin."))
        if "startup" in d:
            n = d["startup"]
            add(n <= 15, f"Açılışta çalışan program: {n}." + ("" if n <= 15 else " Çok fazla; açılışı yavaşlatır."))
        add(not d.get("reboot"), "Yeniden başlatma: " + ("gerekmiyor." if not d.get("reboot")
                                                      else "bekleyen güncelleme var; yeniden başlatın."))
        if d.get("lastUpdate"):
            try:
                import datetime
                age = (datetime.date.today() - datetime.date.fromisoformat(d["lastUpdate"])).days
                add(age <= 45, f"Son güncelleme: {d['lastUpdate']} ({age} gün önce)." +
                    ("" if age <= 45 else " Windows Update'i kontrol edin."))
            except Exception:
                pass

        verdict = ("MÜKEMMEL — bilgisayarınız sağlıklı görünüyor." if warns == 0 else
                   f"DİKKAT — {warns} konuya bakmanız önerilir." if warns <= 3 else
                   f"KÖTÜ — {warns} sorun bulundu; müdahale gerekli.")
        head = (f"GENEL SAĞLIK RAPORU   {time.strftime('%d.%m.%Y %H:%M')}\n" + "=" * 60 +
                f"\nSonuç: {verdict}\n" + "=" * 60 + "\n\n")
        return head + "\n".join(lines) + "\n\n✔ = sorun yok     ⚠ = bakmanız gerekir"

    # ------------------------------ resmi web ----------------------------
    def _open_program_url(self, action):
        if action == "url_brand_drivers":
            name = (self.brand or "").lower()
            url = next((u for k, u in BRAND_URLS.items() if k in name), None)
            if not url:
                q = f"{self.brand} {self.model} driver download".replace(" ", "+")
                url = f"https://www.google.com/search?q={q}"
        else:
            url = URLS.get(action)
        if url:
            open_url(url)
            self._log(f"Resmi sayfa açıldı: {url}")
            self.status.configure(text="● RESMİ SAYFA AÇILDI", fg=CYAN)

    # ------------------------------ canlı izleme -------------------------
    def _tick_metrics(self):
        try:
            cpu = cpu_percent()
            ram, used, total = memory_status()
            du = shutil.disk_usage(self.sysdrive)
            disk = du.used / du.total * 100
            up = uptime_seconds()
            bat = battery_status()
            self.header_stats.configure(text=f"CPU %{cpu:.0f}    RAM %{ram:.0f}    DISK %{disk:.0f}")
            if self.gauges:
                self.gauges["cpu"].set(cpu, f"%{cpu:.0f}", "Toplam işlemci yükü")
                self.gauges["ram"].set(ram, f"%{ram:.0f}", f"{used:.1f} / {total:.1f} GB")
                self.gauges["disk"].set(disk, f"%{disk:.0f}", f"{du.free / 1024 ** 3:.0f} GB boş")
                if bat:
                    pct, ac = bat
                    self.gauges["pwr"].set(pct, f"%{pct}" + (" ⚡" if ac else ""),
                                           "Şarj oluyor" if ac else "Pille çalışıyor")
                else:
                    self.gauges["pwr"].set(100, "AC", "Şebeke gücü (pil yok)")
            if self.info_vars:
                self.info_vars["uptime"].set(fmt_uptime(up))
                self.info_vars["mem"].set(f"{used:.1f} / {total:.1f} GB")
                self.info_vars["free"].set(f"{du.free / 1024 ** 3:.0f} GB")
                self.info_vars["user"].set(os.environ.get("USERNAME", "—"))
        except Exception:
            pass
        self.root.after(1000, self._tick_metrics)

    # ------------------------------ günlük / sonuç -----------------------
    def _log(self, text):
        self.log_lines.append(f"[{time.strftime('%H:%M:%S')}] {text}")
        self.log_lines = self.log_lines[-500:]

    def show_log(self):
        w = tk.Toplevel(self.root)
        w.title("aSiKuRT - İşlem Günlüğü")
        w.geometry("850x520")
        w.configure(bg=BG)
        box = scrolledtext.ScrolledText(w, bg="#0A101C", fg="#DDE8F5", insertbackground=CYAN,
                                        font=("Consolas", 9), relief="flat")
        box.pack(fill="both", expand=True, padx=12, pady=12)
        box.insert("1.0", "\n".join(self.log_lines) or "Henüz işlem günlüğü yok.")
        box.configure(state="disabled")
        tk.Button(w, text="Kapat", command=w.destroy, bg=RED, fg="white", relief="flat",
                  padx=16, pady=7).pack(pady=(0, 12))

    def _result_window(self, action, text):
        label, desc, _ = ACTIONS[action]
        w = tk.Toplevel(self.root)
        w.title(f"aSiKuRT - {label}")
        w.geometry("960x640")
        w.configure(bg=BG)
        tk.Label(w, text=f"✓ {label}", font=("Segoe UI", 13, "bold"), fg=GREEN,
                 bg=BG).pack(anchor="w", padx=16, pady=(14, 0))
        tk.Label(w, text=desc, font=("Segoe UI", 9), fg=MUTED, bg=BG, wraplength=900,
                 justify="left").pack(anchor="w", padx=16, pady=(2, 6))
        box = scrolledtext.ScrolledText(w, bg="#090F1A", fg="#D9E4F2", insertbackground=CYAN,
                                        font=("Consolas", 10), relief="flat", wrap="none")
        box.pack(fill="both", expand=True, padx=16, pady=8)
        box.insert("1.0", text or "İşlem tamamlandı.")
        box.configure(state="disabled")

        bar = tk.Frame(w, bg=BG)
        bar.pack(pady=(0, 14))

        def copy():
            self.root.clipboard_clear()
            self.root.clipboard_append(text or "")

        def save():
            name = re.sub(r"[^\w\-]+", "_", action) + time.strftime("_%H%M%S") + ".txt"
            path = os.path.join(self._desktop(), "aSiKuRT_" + name)
            Path(path).write_text(text or "", encoding="utf-8", errors="ignore")
            messagebox.showinfo("Kaydedildi", f"Masaüstüne kaydedildi:\n{path}", parent=w)

        for t, cmd_ in (("Kopyala", copy), ("Masaüstüne kaydet", save), ("Kapat", w.destroy)):
            tk.Button(bar, text=t, command=cmd_, bg=BTN, fg=WHITE, activebackground=CYAN,
                      activeforeground="#081018", relief="flat", padx=18,
                      pady=8).pack(side="left", padx=6)

    def _poll_events(self):
        try:
            while True:
                e = self.event_queue.get_nowait()
                if e[0] == "ok":
                    _, action, result = e
                    self.busy = False
                    self.progress.stop()
                    self.status.configure(text=f"● TAMAMLANDI: {ACTIONS[action][0]}", fg=GREEN)
                    self.header_sub.configure(text="İşlem tamamlandı.")
                    self._log(f"{action}: tamamlandı")
                    self._result_window(action, result)
                elif e[0] == "err":
                    _, action, error = e
                    self.busy = False
                    self.progress.stop()
                    self.status.configure(text=f"● HATA: {ACTIONS[action][0]}", fg=RED)
                    self.header_sub.configure(text="İşlem hata verdi.")
                    self._log(f"{action}: HATA")
                    messagebox.showerror("İşlem Hatası", error)
                elif e[0] == "brand":
                    _, self.brand, self.model = e
                    self.brand_label.configure(text=f"{self.brand}  •  {self.model}")
        except queue.Empty:
            pass
        self.root.after(150, self._poll_events)

    def _on_close(self):
        if self.busy and not messagebox.askyesno(
                "İşlem devam ediyor",
                "Bir işlem çalışıyor. Programı kapatmak istediğinizden emin misiniz?"):
            return
        self.root.destroy()


def main():
    if os.name != "nt":
        messagebox.showerror("Windows Gerekli", "Bu program Windows 10/11 için tasarlanmıştır.")
        return
    elevate_to_admin()  # reddedilirse kullanıcı modunda devam eder
    try:
        root = tk.Tk()
        ProITDashboard(root)
        root.mainloop()
    except Exception:
        try:
            messagebox.showerror("Kritik Hata", traceback.format_exc())
        except Exception:
            print(traceback.format_exc())


if __name__ == "__main__":
    main()
