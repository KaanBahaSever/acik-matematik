<script setup>
import { ref, computed } from 'vue'

// Girdi verileri için reaktif durum yöneticileri
const inputText = ref('MATH')
const shiftKey = ref(3)
const isEncryptMode = ref(true)

const processedText = computed(() => {
  let outputString = ''
  const rawText = inputText.value.toUpperCase()
  const k = shiftKey.value

  for (let i = 0; i < rawText.length; i++) {
    const charCode = rawText.charCodeAt(i)

    // Sadece standart İngilizce alfabesini işleme dahil et (ASCII 65-90)
    if (charCode >= 65 && charCode <= 90) {
      const x = charCode - 65
      let newX

      if (isEncryptMode.value) {
        newX = (x + k) % 26 // Şifreleme kuralı
      } else {
        newX = (x - k) % 26 // Deşifreleme kuralı
        if (newX < 0) newX += 26 // Negatif modül dengelemesi
      }

      outputString += String.fromCharCode(newX + 65)
    } else {
      // Sayıları, boşlukları ve yabancı karakterleri olduğu gibi aktar
      outputString += rawText[i]
    }
  }
  return outputString
})
</script>

<template>
  <div class="custom-block info" style="padding-top: 20px;">
    <p style="font-size: 1.2em; font-weight: bold; margin-bottom: 15px; text-align: center;">🧮 Canlı Sezar Hesaplayıcı
    </p>
    <div style="display: flex; flex-direction: column; gap: 15px;">
      <label>
        <strong style="color: var(--vp-c-text-1);">İşlem Türü:</strong><br>
        <select v-model="isEncryptMode"
          style="width: 100%; padding: 8px; margin-top: 5px; border-radius: 6px; border: 1px solid var(--vp-c-divider); background: var(--vp-c-bg-alt); color: var(--vp-c-text-1);">
          <option :value="true">🔒 Şifrele (Encrypt)</option>
          <option :value="false">🔓 Deşifrele (Decrypt)</option>
        </select>
      </label>

      <label>
        <strong style="color: var(--vp-c-text-1);">Anahtar (k = {{ shiftKey }}):</strong><br>
        <input type="range" v-model.number="shiftKey" min="0" max="25" style="width: 100%; margin-top: 5px;">
      </label>

      <label>
        <strong style="color: var(--vp-c-text-1);">Mesaj:</strong><br>
        <input type="text" v-model="inputText" placeholder="Şifrelenecek veya çözülecek mesaj..."
          style="width: 100%; padding: 8px; margin-top: 5px; border-radius: 6px; border: 1px solid var(--vp-c-divider); background: var(--vp-c-bg-alt); color: var(--vp-c-text-1);">
      </label>

      <div
        style="margin-top: 10px; padding: 20px; background: var(--vp-c-bg-mute); border-radius: 8px; text-align: center; border: 1px solid var(--vp-c-divider);">
        <span
          style="font-size: 0.9em; color: var(--vp-c-text-2); text-transform: uppercase; letter-spacing: 1px;">Sonuç</span><br>
        <strong style="font-size: 1.8em; letter-spacing: 3px; color: var(--vp-c-brand); word-break: break-all;">{{
          processedText || '...' }}</strong>
      </div>
    </div>
  </div>
</template>