# Guide d'Installation - Global Risk Dashboard

## 🚀 Prérequis

- **Python 3.11+**
- **Docker** (optionnel, pour containerization)
- **Git**
- **pip** ou **poetry**

## Installation locale

### 1. Cloner le repository

```bash
git clone https://github.com/babaforexskalpingfibo-cmd/global-risk-dashboard.git
cd global-risk-dashboard
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv

# Activation (Linux/Mac)
source venv/bin/activate

# Activation (Windows)
venv\\Scripts\\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env avec tes configurations
nano .env
```

### 5. Lancer l'application

```bash
python app.py
```

L'application sera disponible à `http://localhost:5000`

---

## 🐳 Installation avec Docker

### 1. Build l'image Docker

```bash
docker build -t global-risk-dashboard .
```

### 2. Lancer le container

```bash
docker run -p 5000:5000 \\
  --env-file .env \\
  global-risk-dashboard
```

### 3. Docker Compose (recommandé pour production)

```bash
docker-compose up -d
```

---

## ☁️ Déploiement sur Hostinger VPS

### 1. SSH sur ton VPS

```bash
ssh user@your-vps-ip
```

### 2. Installer Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 3. Cloner et déployer

```bash
git clone https://github.com/babaforexskalpingfibo-cmd/global-risk-dashboard.git
cd global-risk-dashboard

# Éditer .env pour production
sudo nano .env

# Lancer avec Docker Compose
sudo docker-compose up -d
```

---

## 🔧 Dépannage

### Port 5000 déjà en utilisation

```bash
python app.py --port 8000
```

### Erreurs d'importation

```bash
pip install --upgrade -r requirements.txt
```

---

## 📊 APIs Intégrées

✅ **GDACS** - Catastrophes naturelles (aucune clé requise)  
✅ **CoinGecko** - Données crypto (aucune clé requise)  
✅ **REST Countries** - Données pays (aucune clé requise)  
⚠️ **ACLED** - Conflits (clé optionnelle)

---

## 📝 Logs

Vérifier les logs Flask :

```bash
# En local
tail -f app.log

# Avec Docker
docker logs -f global-risk-dashboard
```
