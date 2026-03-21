"""
==========================================================================
 HR FACE UTILS - Utilitas Face Recognition & Validasi Lokasi GPS
==========================================================================
 File ini berisi utility functions untuk fitur absensi biometrik:

 1. LOCATION UTILITIES (Validasi GPS):
    - haversine_distance() → Hitung jarak 2 titik GPS (meter)
    - validate_location()  → Cek apakah user dalam radius kantor

 2. FACE DETECTION (Deteksi Wajah):
    - detect_face()         → Deteksi wajah dalam gambar (Haar Cascade)
    - image_to_array()      → Konversi file gambar → numpy array
    - base64_to_array()     → Konversi base64 → numpy array

 3. FACE ENCODING (Encoding Wajah):
    - encode_face()         → Generate encoding dari gambar wajah
    - encode_face_from_file()    → Encode dari file upload
    - encode_face_from_base64()  → Encode dari base64 string

 4. FACE COMPARISON (Perbandingan Wajah):
    - compare_faces()           → Bandingkan 2 encoding (histogram + ORB)
    - find_matching_karyawan()  → Cari karyawan yang cocok dari wajah
    - validate_face_exists()    → Validasi ada wajah di gambar

 Teknologi:
 - OpenCV (cv2) → Haar Cascade + ORB Feature Descriptor
 - LBPH (Local Binary Patterns Histogram) untuk encoding
 - Haversine Formula untuk kalkulasi jarak GPS

 Terhubung dengan:
 - hr/models.py → Karyawan, FotoWajah (model data wajah)
 - hr/views.py → API endpoint absensi
==========================================================================
"""
import cv2
import numpy as np
import base64
import json
import os
import math
from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)


# ==================== LOCATION UTILITIES ====================

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Menghitung jarak antara dua koordinat GPS menggunakan rumus Haversine
    Args:
        lat1, lon1: Koordinat titik pertama (latitude, longitude dalam derajat)
        lat2, lon2: Koordinat titik kedua (latitude, longitude dalam derajat)
    Returns:
        Jarak dalam meter
    """
    # Radius bumi dalam meter
    R = 6371000
    
    # Konversi ke radian
    lat1_rad = math.radians(float(lat1))
    lat2_rad = math.radians(float(lat2))
    delta_lat = math.radians(float(lat2) - float(lat1))
    delta_lon = math.radians(float(lon2) - float(lon1))
    
    # Formula Haversine
    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def validate_location(user_lat, user_lon, office_lat, office_lon, radius_meters):
    """
    Validasi apakah lokasi user dalam radius kantor
    Args:
        user_lat, user_lon: Koordinat user
        office_lat, office_lon: Koordinat kantor
        radius_meters: Radius maksimal dalam meter
    Returns:
        (is_valid: bool, distance: float, message: str)
    """
    try:
        if not all([user_lat, user_lon, office_lat, office_lon]):
            return True, 0, "Koordinat tidak lengkap, validasi dilewati"
        
        distance = haversine_distance(user_lat, user_lon, office_lat, office_lon)
        distance_rounded = round(distance, 1)
        
        if distance <= radius_meters:
            return True, distance_rounded, f"Lokasi valid, jarak {distance_rounded}m dari kantor"
        else:
            return False, distance_rounded, f"Lokasi di luar jangkauan! Jarak {distance_rounded}m, maksimal {radius_meters}m"
    # Tangkap error Exception — lanjutkan tanpa crash
    except Exception as e:
        logger.error(f"Error validasi lokasi: {e}")
        return True, 0, f"Error validasi lokasi: {str(e)}"


# ==================== FACE DETECTION UTILITIES ====================

# Path ke Haar Cascade untuk deteksi wajah
CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'


def get_face_cascade():
    """Mengambil face cascade classifier"""
    return cv2.CascadeClassifier(CASCADE_PATH)


def image_to_array(image_file):
    """Konversi file gambar ke numpy array"""
    try:
        # Baca file gambar
        if hasattr(image_file, 'read'):
            image_data = image_file.read()
            image_file.seek(0)  # Reset pointer
        else:
            with open(image_file, 'rb') as f:
                image_data = f.read()
        
        # Konversi ke numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    # Tangkap error Exception — lanjutkan tanpa crash
    except Exception as e:
        logger.error(f"Error konversi gambar: {e}")
        return None


def base64_to_array(base64_string):
    """Konversi base64 string ke numpy array"""
    try:
        # Hapus header data URI jika ada
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    # Tangkap error Exception — lanjutkan tanpa crash
    except Exception as e:
        logger.error(f"Error konversi base64: {e}")
        return None


def detect_face(image):
    """
    Mendeteksi wajah dalam gambar
    Returns: (face_image, face_rect) atau (None, None) jika tidak ada wajah
    """
    if image is None:
        return None, None
    
    face_cascade = get_face_cascade()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Deteksi wajah
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(100, 100)
    )
    
    if len(faces) == 0:
        return None, None
    
    # Ambil wajah terbesar
    largest_face = max(faces, key=lambda f: f[2] * f[3])
    x, y, w, h = largest_face
    
    # Crop dan resize wajah
    face_img = gray[y:y+h, x:x+w]
    face_img = cv2.resize(face_img, (200, 200))
    
    return face_img, largest_face


def encode_face(image):
    """
    Generate encoding dari gambar wajah
    Returns: JSON string encoding atau None jika gagal
    """
    try:
        face_img, rect = detect_face(image)
        if face_img is None:
            return None
        
        # Gunakan histogram sebagai encoding sederhana
        # LBPH membutuhkan training, jadi kita simpan histogram face
        hist = cv2.calcHist([face_img], [0], None, [256], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        
        # Simpan juga feature dari wajah menggunakan ORB
        orb = cv2.ORB_create(nfeatures=128)
        keypoints, descriptors = orb.detectAndCompute(face_img, None)
        
        encoding = {
            'histogram': hist.tolist(),
            'descriptors': descriptors.tolist() if descriptors is not None else None,
            'face_size': face_img.shape
        }
        
        return json.dumps(encoding)
    # Tangkap error Exception — lanjutkan tanpa crash
    except Exception as e:
        logger.error(f"Error encoding wajah: {e}")
        return None


def encode_face_from_file(image_file):
    """Encode wajah dari file upload"""
    img = image_to_array(image_file)
    if img is None:
        return None
    return encode_face(img)


def encode_face_from_base64(base64_string):
    """Encode wajah dari base64 string"""
    img = base64_to_array(base64_string)
    if img is None:
        return None
    return encode_face(img)


def compare_faces(encoding1_json, encoding2_json, threshold=0.65):
    """
    Membandingkan dua encoding wajah
    Returns: (match: bool, confidence: float)
    """
    try:
        if not encoding1_json or not encoding2_json:
            return False, 0.0
        
        enc1 = json.loads(encoding1_json)
        enc2 = json.loads(encoding2_json)
        
        # Bandingkan histogram dengan correlation
        hist1 = np.array(enc1['histogram'])
        hist2 = np.array(enc2['histogram'])
        
        correlation = cv2.compareHist(
            hist1.astype(np.float32), 
            hist2.astype(np.float32), 
            cv2.HISTCMP_CORREL
        )
        
        # Jika ada descriptors, bandingkan juga
        desc_match = 0.5  # Default jika tidak ada descriptor
        if enc1.get('descriptors') and enc2.get('descriptors'):
            desc1 = np.array(enc1['descriptors'], dtype=np.uint8)
            desc2 = np.array(enc2['descriptors'], dtype=np.uint8)
            
            # Gunakan BFMatcher
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            # Blok penanganan error — coba jalankan kode di bawah
            try:
                matches = bf.match(desc1, desc2)
                if len(matches) > 0:
                    # Hitung persentase match
                    good_matches = [m for m in matches if m.distance < 50]
                    desc_match = len(good_matches) / max(len(desc1), len(desc2))
            except:
                pass
        
        # Gabungkan score (60% histogram, 40% descriptor)
        confidence = (correlation * 0.6) + (desc_match * 0.4)
        confidence = max(0, min(1, confidence))  # Clamp ke 0-1
        
        return confidence >= threshold, confidence
        
    # Tangkap error Exception — lanjutkan tanpa crash
    except Exception as e:
        logger.error(f"Error comparing faces: {e}")
        return False, 0.0


def find_matching_karyawan(image, karyawan_list, threshold=0.55):
    """
    Mencari karyawan yang cocok dari gambar wajah
    Args:
        image: numpy array gambar atau base64 string
        karyawan_list: QuerySet karyawan dengan foto_wajah_set
        threshold: minimum confidence untuk match
    Returns:
        (karyawan, confidence) atau (None, 0.0)
    """
    try:
        # Konversi image jika perlu
        if isinstance(image, str):
            img = base64_to_array(image)
        else:
            img = image
        
        if img is None:
            return None, 0.0
        
        # Encode wajah dari gambar input
        input_encoding = encode_face(img)
        if not input_encoding:
            return None, 0.0
        
        best_match = None
        best_confidence = 0.0
        
        # Loop semua karyawan dan wajah terdaftar
        for karyawan in karyawan_list:
            foto_wajah_list = karyawan.foto_wajah_set.filter(aktif=True)
            
            for foto_wajah in foto_wajah_list:
                if foto_wajah.encoding:
                    match, confidence = compare_faces(
                        input_encoding, 
                        foto_wajah.encoding, 
                        threshold
                    )
                    
                    if match and confidence > best_confidence:
                        best_match = karyawan
                        best_confidence = confidence
        
        return best_match, best_confidence
        
    # Tangkap error Exception — lanjutkan tanpa crash
    except Exception as e:
        logger.error(f"Error finding matching karyawan: {e}")
        return None, 0.0


def validate_face_exists(image):
    """
    Validasi apakah ada wajah di gambar
    Returns: (has_face: bool, face_rect: tuple or None)
    """
    if isinstance(image, str):
        img = base64_to_array(image)
    else:
        img = image
    
    if img is None:
        return False, None
    
    face_img, rect = detect_face(img)
    return face_img is not None, rect
