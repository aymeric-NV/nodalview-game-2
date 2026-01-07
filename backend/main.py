from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import random
from typing import List

app = FastAPI()

# Configuration CORS (Indispensable pour le frontend)
origins = ["http://localhost:5173", "http://127.0.0.1:5173","https://nodalview-game-2.vercel.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- DATA LEÇONS (Le Codex) ---
LESSONS_DATA = [
    {
        "id": 1,
        "title": "Le Shift",
        "icon": "fa-bolt",
        "color": "#f59e0b",
        "content": """
            <h3>Le Changement de Paradigme</h3>
            <p>Le marché est entré dans une ère d'exigence client. L'image a pris le pouvoir et l'IA est devenue un standard.</p>
            <div class='lesson-box'>
                <strong>Les 3 réalités du basculement :</strong>
                <ul>
                    <li>L'image est le premier gage de professionnalisme.</li>
                    <li>L'IA n'est plus un gadget mais un standard attendu (transparence).</li>
                    <li>Exigence d'efficacité : Les clients refusent les visites inutiles.</li>
                </ul>
            </div>
        """
    },
    {
        "id": 2,
        "title": "Ennemis & Survivants",
        "icon": "fa-skull-crossbones",
        "color": "#ef4444",
        "content": """
            <h3>Le Combat des deux mondes</h3>
            <p><strong>Les Ennemis (L'ancien monde) :</strong></p>
            <ul>
                <li>Les agents qui font des photos "à la va-vite".</li>
                <li>L'accumulation d'outils bon marché et éparpillés.</li>
            </ul>
            <br>
            <p><strong>Les Survivants (Le nouveau monde) :</strong></p>
            <ul>
                <li>Ceux qui embrassent le changement et l'IA.</li>
                <li>Ceux qui replacent la transparence au cœur de la relation.</li>
            </ul>
        """
    },
    {
        "id": 3,
        "title": "Magic Potion",
        "icon": "fa-flask",
        "color": "#8b5cf6",
        "content": """
            <h3>La solution Nodalview (5-en-1)</h3>
            <p>Photos HDR, Vidéos, Visites 360°, Plans 2D, Home Staging Virtuel.</p>
            <div class='lesson-box'>
                <strong>L'ingrédient secret :</strong><br>
                Simplicité + Tout-en-un + Spécialisation Immo + IA Responsable.
            </div>
        """
    },
    {
        "id": 4,
        "title": "Promised State",
        "icon": "fa-mountain-sun",
        "color": "#10b981",
        "content": """
            <h3>Le succès selon Nodalview</h3>
            <ul>
                <li><strong>Agent :</strong> Temps réinvesti dans le conseil et les visites qualifiées.</li>
                <li><strong>Vendeur :</strong> Bien vendu plus vite grâce à une valorisation pro.</li>
                <li><strong>Agence :</strong> Une vitrine qui inspire confiance.</li>
            </ul>
        """
    },
    {
        "id": 5,
        "title": "Super Powers",
        "icon": "fa-rocket",
        "color": "#1d4ed8",
        "content": """
            <h3>Vos nouveaux pouvoirs</h3>
            <ul>
                <li><strong>Effet Waouh :</strong> Décrocher l'exclusivité.</li>
                <li><strong>Qualification :</strong> Les acquéreurs s'auto-qualifient.</li>
                <li><strong>Autonomie :</strong> Un rendu pro depuis un simple smartphone.</li>
            </ul>
        """
    }
]
# --- DATA QUIZ---# 
QUIZ_DATA = [
    {
        "question": "Quel est le changement majeur qui s'opère actuellement sur le marché immobilier ?",
        "options": [
            "Les prix de l'immobilier s'effondrent.",
            "L'entrée dans une ère d'exigence client où l'image prend le pouvoir.",
            "Les clients préfèrent visiter des agences physiques uniquement.",
            "La disparition des agents immobiliers au profit des robots."
        ],
        "answer": "L'entrée dans une ère d'exigence client où l'image prend le pouvoir.",
        "explanation": "Les acquéreurs attendent une expérience fluide. L'image est devenue le premier gage de confiance et de professionnalisme."
    },
    {
        "question": "Quelles sont les 3 réalités du basculement du marché ?",
        "options": [
            "L'image reine, l'IA standard, l'exigence d'efficacité.",
            "La baisse des taux, la hausse des prix, la pénurie de biens.",
            "Le drone, la vidéo 4K, le métavers.",
            "La fin du mandat exclusif, l'uberisation, la location."
        ],
        "answer": "L'image reine, l'IA standard, l'exigence d'efficacité.",
        "explanation": "L'image gage de pro, l'IA comme standard attendu, et le refus des visites inutiles."
    },
    {
        "question": "Il existe un 'Gap' (fossé) sur le marché. Entre qui et qui ?",
        "options": [
            "Entre les vendeurs et les acheteurs.",
            "Entre les attentes des clients et ce que proposent encore beaucoup d'agents.",
            "Entre les banques et les agences.",
            "Entre Paris et la province."
        ],
        "answer": "Entre les attentes des clients et ce que proposent encore beaucoup d'agents.",
        "explanation": "Les clients veulent de l'instantané et du qualitatif, l'agent est souvent freiné par des outils obsolètes."
    },
    {
        "question": "Lequel de ces comportements est un 'Ennemi' (Old World) ?",
        "options": [
            "Utiliser trop de lumière naturelle.",
            "Shooter à la 'va-vite' avec des photos amateurs.",
            "Collaborer avec des notaires.",
            "Faire trop de visites physiques qualifiées."
        ],
        "answer": "Shooter à la 'va-vite' avec des photos amateurs.",
        "explanation": "Les photos amateurs et l'accumulation d'outils éparpillés maintiennent les professionnels dans l'ancien monde."
    },
    {
        "question": "Pourquoi l'accumulation d'outils bon marché est-elle un problème ?",
        "options": [
            "Cela coûte trop cher.",
            "Cela crée une perte de temps et de fluidité.",
            "C'est trop moderne.",
            "Les clients n'aiment pas la technologie."
        ],
        "answer": "Cela crée une perte de temps et de fluidité.",
        "explanation": "Jongler entre plusieurs solutions non connectées est une perte d'efficacité majeure (l'ennemi)."
    },
    {
        "question": "Quels sont les piliers de la solution 'Magic Potion' de Nodalview ?",
        "options": [
            "Photo, Vidéo, Drone, Site Web, Publicité.",
            "Photo, Vidéo, Visite Virtuelle, Plans 2D, Home Staging.",
            "Estimation, Vente, Location, Gestion, Syndic.",
            "Facebook, Instagram, LinkedIn, TikTok, YouTube."
        ],
        "answer": "Photo, Vidéo, Visite Virtuelle, Plans 2D, Home Staging.",
        "explanation": "C'est la solution 5-en-1 qui permet de créer, embellir et promouvoir les biens au même endroit."
    },
    {
        "question": "Pourquoi l'IA de Nodalview est-elle unique ?",
        "options": [
            "C'est une IA générique.",
            "C'est une IA entraînée spécifiquement sur l'immobilier et responsable.",
            "Elle remplace l'agent immobilier.",
            "Elle coûte très cher."
        ],
        "answer": "C'est une IA entraînée spécifiquement sur l'immobilier et responsable.",
        "explanation": "Elle garantit un résultat réaliste et transparent, sans fausser la réalité du bien."
    },
    {
        "question": "Quel est l'avantage de l'écosystème 'Mobile + Plateforme' ?",
        "options": [
            "Aucun, c'est compliqué.",
            "L'autonomie et la fluidité de travail.",
            "Cela oblige à avoir deux abonnements.",
            "C'est réservé aux jeunes agents."
        ],
        "answer": "L'autonomie et la fluidité de travail.",
        "explanation": "L'agent peut shooter sur le terrain et gérer/diffuser depuis le bureau instantanément."
    },
    {
        "question": "Dans le 'Promised State', comment l'agent utilise-t-il son temps ?",
        "options": [
            "Il fait de la retouche photo manuelle.",
            "Il se concentre sur le conseil, la négo et les visites qualifiées.",
            "Il gère l'informatique de l'agence.",
            "Il fait visiter des biens à des curieux."
        ],
        "answer": "Il se concentre sur le conseil, la négo et les visites qualifiées.",
        "explanation": "L'objectif est de libérer l'agent des tâches techniques."
    },
    {
        "question": "Quel 'Super Pouvoir' apporte l'outil concernant le matériel ?",
        "options": [
            "Il nécessite un appareil reflex à 2000€.",
            "Il permet un rendu professionnel directement depuis un smartphone.",
            "Il demande un studio photo.",
            "Il faut un drone obligatoirement."
        ],
        "answer": "Il permet un rendu professionnel directement depuis un smartphone.",
        "explanation": "Sans compétences techniques, l'agent obtient un rendu pro avec l'outil qu'il a déjà dans sa poche."
    },
    {
        "question": "Quel est l'impact concret de la 'Qualification' par l'image ?",
        "options": [
            "Aucun.",
            "Les acheteurs s'auto-qualifient, évitant les visites inutiles.",
            "Cela empêche les gens d'appeler.",
            "Cela remplace la visite réelle."
        ],
        "answer": "Les acheteurs s'auto-qualifient, évitant les visites inutiles.",
        "explanation": "Une annonce riche agit comme un filtre : une visite physique devient une confirmation d'achat."
    },
    {
        "question": "Quelle urgence (Bigger Stake) y a-t-il à moderniser sa vitrine ?",
        "options": [
            "Aucune, le marché est calme.",
            "Si vos visuels sont amateurs, le vendeur choisit la concurrence.",
            "C'est juste pour faire joli.",
            "L'urgence est d'imprimer des flyers."
        ],
        "answer": "Si vos visuels sont amateurs, le vendeur choisit la concurrence.",
        "explanation": "L'inertie mène à la disparition. Une mauvaise image fait fuir les mandats exclusifs."
    },
    {
        "question": "Quelle valeur la transparence apporte-t-elle (Survivants) ?",
        "options": [
            "Elle fait peur aux acheteurs.",
            "Elle rassure et engage l'acheteur dès la première impression.",
            "Elle est inutile.",
            "Elle permet de cacher les défauts."
        ],
        "answer": "Elle rassure et engage l'acheteur dès la première impression.",
        "explanation": "La transparence (visite virtuelle, plans) crée la confiance nécessaire à la transaction."
    },
    {
        "question": "Quel rôle Nodalview joue-t-il pour l'agent (Sales Pitch) ?",
        "options": [
            "Le patron de l'agent.",
            "Son assistant marketing qui gère la complexité visuelle.",
            "Son concurrent.",
            "Un simple fournisseur d'hébergement."
        ],
        "answer": "Son assistant marketing qui gère la complexité visuelle.",
        "explanation": "Nodalview prend en charge la technique pour que l'agent se focalise sur l'humain."
    },
    {
        "question": "Quels chiffres prouvent le succès de cette approche ?",
        "options": [
            "100 clients.",
            "22 000 clients satisfaits et 10 ans d'existence.",
            "Une start-up de 6 mois.",
            "Note de 3/5 sur Google."
        ],
        "answer": "22 000 clients satisfaits et 10 ans d'existence.",
        "explanation": "La preuve par le nombre et la durée (Scale & Trust)."
    }
]


LEADERBOARD_FILE = "leaderboard.json"

# --- UTILITAIRES ---
def load_leaderboard_data():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    with open(LEADERBOARD_FILE, "r") as f:
        return json.load(f)

def save_leaderboard_data(data):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(data, f)

# --- ENDPOINTS ---
@app.get("/quiz")
def get_quiz():
    # Clone questions to avoid mutating the base data, then shuffle questions and options
    data = [{**q, "options": q["options"][:]} for q in QUIZ_DATA]
    random.shuffle(data)
    for q in data:
        random.shuffle(q["options"])
    return data

@app.get("/lessons")
def get_lessons():
    return LESSONS_DATA

@app.get("/leaderboard")
def get_leaderboard():
    data = load_leaderboard_data()
    # Trier par score décroissant
    sorted_data = sorted(data, key=lambda x: x['score'], reverse=True)
    return sorted_data[:50]  # Top 50

class ScoreSubmission(BaseModel):
    username: str
    avatar: str
    color: str
    score: int

@app.post("/submit-score")
def submit_score(submission: ScoreSubmission):
    data = load_leaderboard_data()
    # Ajouter le nouveau score
    new_entry = submission.dict()
    data.append(new_entry)
    save_leaderboard_data(data)
    return {"status": "success"}