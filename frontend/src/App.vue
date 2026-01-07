<script setup>
import { ref, computed } from 'vue'
import confetti from 'canvas-confetti'

// --- ÉTAT GLOBAL ---
const screen = ref('onboarding') // Écrans possibles: 'onboarding', 'menu', 'game', 'leaderboard', 'learn'
const user = ref({ name: '', avatar: 'fa-user-astronaut', color: '#1d4ed8' })
const lessons = ref([])
const activeLessonId = ref(1)

// --- AVATARS DISPONIBLES ---
const avatars = [
  'fa-user-astronaut', 'fa-dragon', 'fa-helmet-safety',
  'fa-robot', 'fa-ghost', 'fa-user-ninja'
]
const colors = ['#1d4ed8', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']

// --- EFFETS VISUELS ---
const triggerConfetti = () => {
  confetti({
    particleCount: 150,
    spread: 70,
    origin: { y: 0.6 },
    colors: ['#1d4ed8', '#ef4444', '#10b981', '#f59e0b'] // Tes couleurs
  })
}

const triggerMiniConfetti = () => {
  confetti({
    particleCount: 30,
    spread: 50,
    origin: { y: 0.7 },
    scalar: 0.8
  })
}

// --- ÉTAT DU JEU ---
const questions = ref([])
const currentQuestionIndex = ref(0)
const score = ref(0)
const streak = ref(0)
const leaderboard = ref([])
const loading = ref(false)
const inputError = ref(false)

const hasQuestions = computed(() => questions.value.length > 0)
const canShowNav = computed(() => screen.value !== 'onboarding')
const navItems = [
  { id: 'menu', label: 'QG', icon: 'fa-compass' },
  { id: 'learn', label: 'Codex', icon: 'fa-book-open' },
  { id: 'game', label: 'Quiz', icon: 'fa-gamepad' },
  { id: 'leaderboard', label: 'Hall', icon: 'fa-medal' }
]

// --- ACTIONS ---

// 1. LOGIN
const login = () => {
  if (user.value.name.trim()) {
    inputError.value = false // Reset erreur
    screen.value = 'menu'
  } else {
    inputError.value = true // Déclenche le rouge et le tremblement
    
    // Petit hack pour pouvoir re-trembler si on clique plusieurs fois
    setTimeout(() => { inputError.value = false }, 500) // On enlève l'anim après 0.5s mais on garde le rouge via CSS si besoin (ici je fais simple)
  }
}

// 2. LANCER LE JEU
const startGame = async () => {
  loading.value = true
  try {
    const res = await fetch('http://127.0.0.1:8000/quiz')
    questions.value = await res.json()
    // Reset state
    currentQuestionIndex.value = 0
    score.value = 0
    streak.value = 0
    loading.value = false
    screen.value = 'game'
  } catch (e) {
    alert('Erreur connexion serveur Python 🔴')
    loading.value = false
  }
}

// 3. JOUER UN TOUR
// --- NOUVEL ÉTAT POUR LE FEEDBACK ---
const showFeedback = ref(false)
const feedbackData = ref({ 
  isCorrect: false, 
  correctAnswer: '', 
  explanation: '' 
})

// 3. JOUER UN TOUR (Modifié)
const handleAnswer = (option) => {
  const q = questions.value[currentQuestionIndex.value]
  const isCorrect = (option === q.answer)
  
  // 1. Calcul des points (en arrière-plan)
  if (isCorrect) {
    streak.value++
    const bonus = streak.value > 2 ? 50 : 0
    score.value += (100 + bonus)
    if (streak.value > 1) triggerMiniConfetti()
  } else {
    streak.value = 0
  }

  // 2. Préparer la belle fenêtre (au lieu de l'alerte moche)
  feedbackData.value = {
    isCorrect: isCorrect,
    correctAnswer: q.answer,
    explanation: q.explanation
  }
  showFeedback.value = true // Affiche la modale
}

// 4. PASSER À LA SUITE (Appelé uniquement par le bouton "Continuer")
const nextQuestion = () => {
  showFeedback.value = false // On ferme la fenêtre
  
  // On vérifie s'il reste des questions
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++ // On avance de 1
  } else {
    endGame() // C'est fini
  }
}

// 4. FIN DE PARTIE
const endGame = async () => {
  loading.value = true
  await fetch('http://127.0.0.1:8000/submit-score', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      username: user.value.name,
      avatar: user.value.avatar,
      color: user.value.color,
      score: score.value
    })
  })
  loading.value = false
  triggerConfetti() // 👈 LE GRAND FINAL
  fetchLeaderboard() // Montre directement le classement
}

// 5. VOIR LE CLASSEMENT
const fetchLeaderboard = async () => {
  loading.value = true
  const res = await fetch('http://127.0.0.1:8000/leaderboard')
  leaderboard.value = await res.json()
  loading.value = false
  screen.value = 'leaderboard'
}
// 6. CHARGER LES LEÇONS (Nouvelle action)
const fetchLessons = async () => {
  loading.value = true
  try {
    const res = await fetch('http://127.0.0.1:8000/lessons')
    lessons.value = await res.json()
    activeLessonId.value = 1 // Reset au premier
    loading.value = false
    screen.value = 'learn'
  } catch (e) {
    alert('Erreur chargement leçons')
    loading.value = false
  }
}

// Fonction utilitaire pour récupérer la leçon active
const activeLessonContent = computed(() => lessons.value.find(l => l.id === activeLessonId.value))

// Utilitaires
const progress = computed(() => {
  if (!questions.value.length) return 0
  return ((currentQuestionIndex.value + 1) / questions.value.length) * 100
})

const navigate = async (target) => {
  if (target === screen.value) return
  if (target === 'menu') {
    screen.value = 'menu'
    return
  }
  if (target === 'leaderboard') {
    await fetchLeaderboard()
    return
  }
  if (target === 'learn') {
    await fetchLessons()
    return
  }
  if (target === 'game') {
    if (!questions.value.length) {
      await startGame()
    } else {
      screen.value = 'game'
    }
  }
}
</script>

<template>
  <div class="app-container">
    
    <header class="top-bar">
      <div v-if="user.name" class="user-pill" :style="{borderColor: user.color}">
        <i :class="['fa-solid', user.avatar]" :style="{color: user.color}"></i>
        <span>{{ user.name }}</span>
      </div>
      <nav v-if="canShowNav" class="nav-bar">
        <button
          v-for="item in navItems"
          :key="item.id"
          class="nav-chip"
          :class="{ active: screen === item.id }"
          @click="navigate(item.id)"
        >
          <i :class="['fa-solid', item.icon]"></i>
          <span>{{ item.label }}</span>
        </button>
      </nav>
      <div v-if="screen !== 'onboarding'" class="mini-score">
        <i class="fa-solid fa-trophy"></i> {{ score }}
      </div>
    </header>
    <main class="content-area">
    <div v-if="screen === 'onboarding'" class="screen fade-in">
      <h1>Mission Nodalview 🚀</h1>
      <p class="subtitle">Identifie-toi !</p>
      
      <div class="card">
        <label>Ton Nom de Code</label>
        
        <div class="input-wrapper">
          <input 
            v-model="user.name" 
            type="text" 
            placeholder="Ex: Agent 007" 
            class="input-field" 
            :class="{ 'input-error': inputError }"
            @input="inputError = false" 
          />
          <p v-if="inputError" class="error-msg">
            <i class="fa-solid fa-circle-exclamation"></i> Identité requise !
          </p>
        </div>
        
        <label>Ton Avatar</label>
        <div class="grid-avatars">
          <div 
            v-for="icon in avatars" 
            :key="icon"
            class="avatar-item"
            :class="{ active: user.avatar === icon }"
            @click="user.avatar = icon"
          >
            <i :class="['fa-solid', icon]"></i>
          </div>
        </div>

        <label>Ta Couleur</label>
        <div class="flex-colors">
          <div 
            v-for="c in colors" 
            :key="c"
            class="color-dot"
            :style="{backgroundColor: c, transform: user.color === c ? 'scale(1.3)' : 'scale(1)'}"
            @click="user.color = c"
          ></div>
        </div>
      </div>

      <button @click="login" class="btn-primary full-width">
        ACCEPTER LA MISSION
      </button>
    </div>

    <div v-else-if="screen === 'menu'" class="screen fade-in">
      <h2 class="text-center">Quartier Général</h2>
      <div class="menu-card secondary" style="margin-bottom: 15px;" @click="fetchLessons">
          <i class="fa-solid fa-book-open big-icon"></i>
          <h3>Le Codex</h3>
          <p>Maîtrise la stratégie</p>
        </div>
      <div class="menu-grid">
        <div class="menu-card" @click="startGame">
          <i class="fa-solid fa-gamepad big-icon"></i>
          <h3>Lancer le Quiz</h3>
          <p>Prouve ta valeur</p>
        </div>
        
        <div class="menu-card secondary" @click="fetchLeaderboard">
          <i class="fa-solid fa-medal big-icon"></i>
          <h3>Hall of Fame</h3>
          <p>Voir les légendes</p>
        </div>
      </div>
    </div>

    <div v-else-if="screen === 'learn'" class="screen fade-in">
      <h2 class="text-center">📚 Le Codex</h2>
      
      <div class="tabs-container">
        <div 
          v-for="l in lessons" 
          :key="l.id"
          class="tab-item"
          :class="{ active: activeLessonId === l.id }"
          @click="activeLessonId = l.id"
          :style="{ borderColor: activeLessonId === l.id ? l.color : 'transparent' }"
        >
          <i :class="['fa-solid', l.icon]" :style="{ color: activeLessonId === l.id ? l.color : '#94a3b8' }"></i>
        </div>
      </div>

      <div v-if="activeLessonContent" class="lesson-card-display fade-in">
        <div class="lesson-header" :style="{ backgroundColor: activeLessonContent.color + '15' }">
          <span class="lesson-tag" :style="{ color: activeLessonContent.color }">Module {{ activeLessonContent.id }}</span>
          <h3 :style="{ color: activeLessonContent.color }">{{ activeLessonContent.title }}</h3>
        </div>
        
        <div class="lesson-body" v-html="activeLessonContent.content"></div>
      </div>

      <button @click="screen = 'menu'" class="btn-secondary full-width mt-20">
        <i class="fa-solid fa-arrow-left"></i> Retour au QG
      </button>
    </div>

    <div v-else-if="screen === 'game'" class="screen fade-in">
      <div class="progress-track">
        <div class="progress-fill" :style="{width: progress + '%'}"></div>
      </div>
      
      <div class="question-header">
        <span class="badge">Question {{ currentQuestionIndex + 1 }} / {{ questions.length }}</span>
        <span class="badge fire" v-if="streak > 1">🔥 {{ streak }}</span>
      </div>

      <div v-if="hasQuestions" class="question-block">
        <h3 class="question-text">{{ questions[currentQuestionIndex].question }}</h3>
        <div class="options-list">
          <button 
            v-for="opt in questions[currentQuestionIndex].options" 
            :key="opt"
            @click="handleAnswer(opt)"
            class="option-btn"
          >
            {{ opt }}
          </button>
        </div>
      </div>
      <div v-else class="loading-note">Chargement du quiz...</div>
    </div>

    <div v-else-if="screen === 'leaderboard'" class="screen fade-in">
      <h2 class="text-center">🏆 Hall of Fame</h2>
      
      <div class="leaderboard-list">
        <div v-for="(entry, index) in leaderboard" :key="index" class="rank-row">
          <div class="rank-num">#{{ index + 1 }}</div>
          <div class="rank-avatar">
            <i :class="['fa-solid', entry.avatar]" :style="{color: entry.color}"></i>
          </div>
          <div class="rank-info">
            <div class="rank-name">{{ entry.username }}</div>
          </div>
          <div class="rank-score">{{ entry.score }} pts</div>
        </div>
      </div>

      <button @click="screen = 'menu'" class="btn-secondary full-width mt-20">
        <i class="fa-solid fa-arrow-left"></i> Retour au QG
      </button>
    </div>
</main>
    <div v-if="showFeedback" class="feedback-overlay">
      <div class="feedback-card" :class="feedbackData.isCorrect ? 'border-success' : 'border-error'">
        
        <div class="feedback-icon" :class="feedbackData.isCorrect ? 'bg-success' : 'bg-error'">
          <i v-if="feedbackData.isCorrect" class="fa-solid fa-check"></i>
          <i v-else class="fa-solid fa-xmark"></i>
        </div>

        <h2 v-if="feedbackData.isCorrect" class="text-success">Excellent !</h2>
        <h2 v-else class="text-error">Oups... Raté !</h2>

        <div class="feedback-content">
          <p v-if="!feedbackData.isCorrect" class="correction">
            La bonne réponse était : <br>
            <strong>{{ feedbackData.correctAnswer }}</strong>
          </p>
          
          <div class="explanation-box">
            <i class="fa-regular fa-lightbulb"></i>
            <span>{{ feedbackData.explanation }}</span>
          </div>
        </div>

        <button 
          @click="nextQuestion" 
          class="btn-primary full-width"
          :class="feedbackData.isCorrect ? 'btn-success' : 'btn-error'"
        >
          CONTINUER <i class="fa-solid fa-arrow-right"></i>
        </button>
      </div>
    </div>

  
  </div>
</template>

<style scoped>
/* --- BASE STYLES --- */
.app-container {
  max-width: 1080px;
  margin: 0 auto;
  min-height: 100vh;
  padding: 20px;
  background-color: #f8fafc;
  font-family: 'Poppins', sans-serif;
  color: #0f172a;
}

/* --- HEADER --- */
.top-bar {
  display: flex; justify-content: space-between; align-items: center;
  gap: 12px;
  margin-bottom: 25px;
}
.user-pill {
  background: white; padding: 6px 12px; border-radius: 20px;
  border: 1px solid #e2e8f0; font-weight: bold; font-size: 0.9em;
  display: flex; align-items: center; gap: 8px;
}
.nav-bar {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  flex: 1;
}
.nav-chip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid #e2e8f0;
  background: white;
  padding: 10px 12px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s;
}
.nav-chip.active {
  border-color: #1d4ed8;
  color: #1d4ed8;
  box-shadow: 0 4px 10px rgba(29, 78, 216, 0.1);
}
.mini-score {
  font-weight: 800; color: #f59e0b;
}

/* --- CARDS & INPUTS --- */
.card {
  background: white; border-radius: 16px; padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}
label {
  display: block; font-weight: 700; margin-bottom: 8px; font-size: 0.9em; text-transform: uppercase; color: #64748b;
}
.input-field {
  width: 100%; padding: 12px; border: 2px solid #e2e8f0; border-radius: 10px;
  font-size: 16px; margin-bottom: 12px; outline: none; transition: 0.2s;
  box-sizing: border-box;
}
.input-field:focus { border-color: #1d4ed8; }

/* --- GRID AVATARS --- */
.grid-avatars {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 20px;
}
.avatar-item {
  background: #f1f5f9; padding: 15px; border-radius: 12px; text-align: center;
  font-size: 1.5em; cursor: pointer; color: #64748b; border: 2px solid transparent;
}
.avatar-item.active {
  background: #eff6ff; border-color: #1d4ed8; color: #1d4ed8;
}

/* --- COLORS --- */
.flex-colors {
  display: flex; gap: 15px; justify-content: center; margin-bottom: 10px;
}
.color-dot {
  width: 30px; height: 30px; border-radius: 50%; cursor: pointer; transition: transform 0.2s;
  border: 2px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

/* --- BUTTONS --- */
.btn-primary {
  background: #1d4ed8; color: white; border: none; padding: 16px; border-radius: 12px;
  font-weight: 800; font-size: 16px; cursor: pointer; width: 100%;
  box-shadow: 0 4px 12px rgba(29, 78, 216, 0.3); transition: transform 0.1s;
}
.btn-primary:active { transform: scale(0.98); }

.btn-secondary {
  background: white; border: 1px solid #cbd5e1; color: #475569; padding: 14px;
  border-radius: 12px; font-weight: 700; cursor: pointer;
}

/* --- MENU --- */
.menu-grid { display: grid; gap: 15px; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); }
.menu-card {
  background: white; padding: 20px; border-radius: 16px; text-align: center;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); cursor: pointer; border: 2px solid transparent;
}
.menu-card:hover { border-color: #1d4ed8; transform: translateY(-2px); transition: 0.2s; }
.big-icon { font-size: 2em; margin-bottom: 10px; color: #1d4ed8; }

/* --- GAME UI --- */
.progress-track {
  height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; margin-bottom: 20px;
}
.progress-fill { height: 100%; background: #10b981; transition: width 0.3s; }

.option-btn {
  display: block; width: 100%; background: white; padding: 18px; margin-bottom: 12px;
  border: 1px solid #e2e8f0; border-radius: 12px; text-align: left; font-weight: 600;
  cursor: pointer; transition: 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.option-btn:hover { border-color: #1d4ed8; background: #f8fafc; }
.question-block { display: flex; flex-direction: column; gap: 12px; }
.options-list { display: grid; gap: 10px; }
.loading-note { color: #64748b; text-align: center; font-weight: 600; }

/* --- LEADERBOARD --- */
.rank-row {
  display: flex; align-items: center; background: white; padding: 12px;
  border-radius: 12px; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.rank-num { font-weight: 800; width: 30px; color: #cbd5e1; }
.rank-avatar { width: 40px; text-align: center; font-size: 1.2em; }
.rank-info { flex-grow: 1; margin-left: 10px; font-weight: 700; }
.rank-score { font-weight: 800; color: #1d4ed8; }

/* --- UTILS --- */
.text-center { text-align: center; }
.mt-20 { margin-top: 20px; }
.full-width { width: 100%; }
.badge {
  background: #e2e8f0; padding: 4px 10px; border-radius: 6px; font-size: 0.8em; font-weight: 700;
}
.badge.fire { background: #fee2e2; color: #ef4444; margin-left: 10px; }
.fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
/* --- FEEDBACK MODAL (Overlay) --- */
.feedback-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(15, 23, 42, 0.6); /* Fond sombre transparent */
  backdrop-filter: blur(4px); /* Effet de flou moderne */
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 20px;
  animation: fadeIn 0.2s ease-out;
}

.feedback-card {
  background: white; width: 100%; max-width: 400px;
  border-radius: 24px; padding: 30px 24px;
  text-align: center; position: relative;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  animation: slideUp 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Effet rebond */
}

/* Animations */
@keyframes slideUp {
  from { opacity: 0; transform: translateY(50px) scale(0.9); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* Couleurs dynamiques */
.border-success { border-bottom: 6px solid #10b981; }
.border-error { border-bottom: 6px solid #ef4444; }

.text-success { color: #10b981; margin: 15px 0; font-family: 'Fugaz One', sans-serif; }
.text-error { color: #ef4444; margin: 15px 0; font-family: 'Fugaz One', sans-serif; }

/* Icône ronde flottante */
.feedback-icon {
  width: 70px; height: 70px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 30px; color: white; margin: -60px auto 10px auto;
  border: 6px solid white; /* Pour couper la carte en haut */
}
.bg-success { background: #10b981; }
.bg-error { background: #ef4444; }

/* Contenu textuel */
.correction { color: #ef4444; margin-bottom: 15px; background: #fef2f2; padding: 10px; border-radius: 8px; font-size: 0.9em; }
.explanation-box {
  background: #f1f5f9; padding: 15px; border-radius: 12px;
  color: #475569; font-size: 0.95em; line-height: 1.5;
  display: flex; gap: 10px; text-align: left; align-items: start;
  margin-bottom: 25px;
}

/* Boutons colorés */
.btn-success { background: #10b981 !important; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4) !important; }
.btn-error { background: #ef4444 !important; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4) !important; }

/* --- VALIDATION & ERREURS --- */

/* Bordure rouge quand erreur */
.input-field.input-error {
  border-color: #ef4444 !important;
  background-color: #fef2f2;
  animation: shake 0.4s cubic-bezier(.36,.07,.19,.97) both;
}

/* Message d'erreur sous l'input */
.error-msg {
  color: #ef4444;
  font-size: 0.85em;
  font-weight: 700;
  margin-top: 0;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 6px;
  animation: fadeIn 0.3s;
}

/* Animation de tremblement (Shake) */
@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}

/* --- LEÇONS (TABS) --- */
.tabs-container {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  /* padding-bottom: 10px;  <-- REMPLACE CETTE LIGNE */
  padding: 5px 5px 15px 5px; /* 👈 NOUVEAU : On met du padding partout (Haut Droite Bas Gauche) */
  margin-bottom: 20px;
  /* Masquer la barre de scroll disgracieuse */
  scrollbar-width: none; 
}
.tabs-container::-webkit-scrollbar { display: none; }

.tab-item {
  min-width: 50px; height: 50px; background: white; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2em; cursor: pointer; border: 2px solid transparent;
  transition: all 0.2s; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  flex-shrink: 0; /* Empêche l'écrasement */
}
.tab-item.active { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }

/* --- CARTE DE LEÇON --- */
.lesson-card-display {
  background: white; border-radius: 20px; overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06); min-height: 300px;
}
.lesson-header { padding: 20px; border-bottom: 1px solid #f1f5f9; }
.lesson-tag { font-weight: 800; text-transform: uppercase; font-size: 0.75em; letter-spacing: 1px; display: block; margin-bottom: 5px;}
.lesson-header h3 { margin: 0; font-size: 1.4em; }

.lesson-body { padding: 25px; line-height: 1.6; color: #334155; }

/* Styles spécifiques pour le contenu HTML injecté via v-html */
:deep(.lesson-body h3) { font-size: 1.1em; color: #0f172a; margin-top: 0; }
:deep(.lesson-body ul) { padding-left: 20px; margin: 15px 0; }
:deep(.lesson-body li) { margin-bottom: 10px; }
:deep(.lesson-box) { 
  background: #f8fafc; padding: 15px; border-radius: 10px; 
  border-left: 4px solid #cbd5e1; margin-top: 20px; font-size: 0.9em;
}

/* --- RESPONSIVE --- */
.content-area { display: block; }

@media (min-width: 640px) {
  .app-container { padding: 32px; }
  .content-area { max-width: 900px; margin: 0 auto; }
  .nav-bar { grid-template-columns: repeat(4, auto); justify-content: flex-end; }
  .nav-chip { padding-inline: 14px; }
  .card, .lesson-card-display, .screen { padding: 24px; }
}

@media (max-width: 639px) {
  .top-bar { flex-direction: column; align-items: stretch; }
  .nav-bar { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}


</style>