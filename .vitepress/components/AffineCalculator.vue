<script setup>
import { ref, computed } from 'vue'

const inputText = ref('MATH')
const aKey = ref(5)
const bKey = ref(8)
const isEncryptMode = ref(true)

// 26 ile aralarında asal olan geçerli 'a' değerleri
const validAKeys = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]

// Mod 26'ya göre çarpımsal tersler sözlüğü (a^-1)
const modInverses = {
  1: 1, 3: 9, 5: 21, 7: 15, 9: 3, 11: 19,
  15: 7, 17: 23, 19: 11, 21: 5, 23: 17, 25: 25
}

const processedText = computed(() => {
  let outputString = ''
  const rawText = inputText.value.toUpperCase()
  const a = aKey.value
  const b = bKey.value
  const aInv = modInverses[a]

  for (let i = 0; i < rawText.length; i++) {
    const charCode = rawText.charCodeAt(i)

    if (charCode >= 65 && charCode <= 90) {
      const x = charCode - 65
      let newX

      if (isEncryptMode.value) {
        // Şifreleme: E(x) = (a*x + b) mod 26
        newX = (a * x + b) % 26
      } else {
        // Deşifreleme: D(y) = a^-1 * (y - b) mod 26
        newX = (aInv * (x - b)) % 26
        // Negatif modül düzeltmesi
        if (newX < 0) {
          newX = (newX % 26) + 26
          newX = newX % 26
        }
      }

      outputString += String.fromCharCode(newX + 65)
    } else {
      outputString += rawText[i]
    }
  }
  return outputString
})
</script>

<template>
<div class="custom-block tip" style="padding-top: 20px;">
  <p style="font-size: 1.2em; font-weight: bold; margin-bottom: 15px; text-align: center;">Canlı Afin Hesaplayıcı</p>
  
  <div style="display: flex; flex-direction: column; gap: 15px;">
    <label>
      <strong style="color: var(--vp-c-text-1);">İşlem Türü:</strong><br>
      <select v-model="isEncryptMode" style="width: 100%; padding: 8px; margin-top: 5px; border-radius: 6px; border: 1px solid var(--vp-c-divider); background: var(--vp-c-bg-alt); color: var(--vp-c-text-1);">
        <option :value="true">🔒 Şifrele (Encrypt)</option>
        <option :value="false">🔓 Deşifrele (Decrypt)</option>
      </select>
    </label>

    <div style="display: flex; gap: 15px;">
      <label style="flex: 1;">
        <strong style="color: var(--vp-c-text-1);">Çarpan (a = {{ aKey }}):</strong><br>
        <select v-model.number="aKey" style="width: 100%; padding: 8px; margin-top: 5px; border-radius: 6px; border: 1px solid var(--vp-c-divider); background: var(--vp-c-bg-alt); color: var(--vp-c-text-1);">
          <option v-for="val in validAKeys" :key="val" :value="val">{{ val }} (Tersi: {{ modInverses[val] }})</option>
        </select>
      </label>

      <label style="flex: 1;">
        <strong style="color: var(--vp-c-text-1);">Kaydırma (b = {{ bKey }}):</strong><br>
        <input type="range" v-model.number="bKey" min="0" max="25" style="width: 100%; margin-top: 15px;">
      </label>
    </div>

    <label>
      <strong style="color: var(--vp-c-text-1);">Mesaj:</strong><br>
      <input type="text" v-model="inputText" placeholder="Şifrelenecek veya çözülecek mesaj..." style="width: 100%; padding: 8px; margin-top: 5px; border-radius: 6px; border: 1px solid var(--vp-c-divider); background: var(--vp-c-bg-alt); color: var(--vp-c-text-1);">
    </label>

    <div style="margin-top: 10px; padding: 20px; background: var(--vp-c-bg-mute); border-radius: 8px; text-align: center; border: 1px solid var(--vp-c-divider);">
      <span style="font-size: 0.9em; color: var(--vp-c-text-2); text-transform: uppercase; letter-spacing: 1px;">Sonuç</span><br>
      <strong style="font-size: 1.8em; letter-spacing: 3px; color: var(--vp-c-brand); word-break: break-all;">{{ processedText || '...' }}</strong>
    </div>
  </div>
</div>
</template>