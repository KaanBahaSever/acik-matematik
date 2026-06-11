<template>
  <div class="math-block calculator">
    <div class="math-block-title">🧮 Legendre Sembolü Hesaplayıcı</div>
    
    <div class="calc-container">
      <div class="input-group">
        <label>Taban (a):</label>
        <input type="number" v-model.number="a" @input="clearResult" placeholder="Örn: 13" />
      </div>
      
      <div class="input-group">
        <label>Modül (p):</label>
        <input type="number" v-model.number="p" @input="clearResult" placeholder="Tek Asal (Örn: 17)" />
      </div>
      
      <button @click="calculate" class="calc-button">Hesapla</button>
      <button @click="reset" class="calc-button calc-button-reset">Sıfırla</button>
    </div>

    <div v-if="error" class="calc-error">
      ⚠️ {{ error }}
    </div>
    
    <div v-if="result !== null && !error" class="calc-result" :class="{ 'calc-result-success': result === 1, 'calc-result-danger': result === -1, 'calc-result-neutral': result === 0 }">
      <div class="result-formula">
        <span>Sonuç: </span>
        <span class="legendre-symbol">
          (
          <div class="fraction">
            <span class="numerator">{{ a }}</span>
            <span class="denominator">{{ p }}</span>
          </div>
          )
        </span>
        <span> = <strong>{{ result }}</strong></span>
      </div>
      
      <div class="calc-meaning">
        <span v-if="result === 1">✅ <strong>{{ a }}</strong>, modülo <strong>{{ p }}</strong>'ye göre bir <strong>Kuadratik Rezidü (KR)</strong>'dür. <span class="math-tex">x<sup>2</sup> &equiv; {{ a }} <span class="math-roman">(mod {{ p }})</span></span> denklemi çözülebilir.</span>
        <span v-if="result === -1">❌ <strong>{{ a }}</strong>, modülo <strong>{{ p }}</strong>'ye göre bir <strong>Kuadratik Non-Rezidü (KNR)</strong>'dür. <span class="math-tex">x<sup>2</sup> &equiv; {{ a }} <span class="math-roman">(mod {{ p }})</span></span> denklemi çözülemez.</span>
        <span v-if="result === 0">ℹ️ <strong>{{ a }}</strong> sayısı, <strong>{{ p }}</strong>'nin bir katıdır (Aralarında asal değiller).</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const a = ref(null)
const p = ref(null)
const result = ref(null)
const error = ref('')

// Asallık testi (Sadece p'nin tek asal olup olmadığını denetler)
const isPrime = (num) => {
  if (num <= 1) return false
  if (num === 2) return true // 2 asaldır ama Legendre için tek asal istiyoruz
  if (num % 2 === 0) return false
  for (let i = 3; i * i <= num; i += 2) {
    if (num % i === 0) return false
  }
  return true
}

// Javascript BigInt ile Hızlı Modüler Üs Alma Algoritması (a^b mod m)
const modPow = (base, exponent, modulus) => {
  if (modulus === 1n) return 0n
  let res = 1n
  let b = BigInt(base) % BigInt(modulus)
  let e = BigInt(exponent)
  const m = BigInt(modulus)

  // Negatif tabanları pozitife çevirme (Örn: a = -1)
  if (b < 0n) b = (b % m) + m

  while (e > 0n) {
    if (e % 2n === 1n) res = (res * b) % m
    e = e / 2n
    b = (b * b) % m
  }
  return res
}

const clearResult = () => {
  result.value = null
  error.value = ''
}

const reset = () => {
  a.value = null
  p.value = null
  result.value = null
  error.value = ''
}

const calculate = () => {
  error.value = ''
  result.value = null

  if (a.value === null || a.value === '' || p.value === null || p.value === '') {
    error.value = 'Lütfen a ve p değerlerini eksiksiz doldurun.'
    return
  }

  if (!Number.isInteger(a.value) || !Number.isInteger(p.value)) {
    error.value = 'a ve p değerleri tam sayı olmalıdır.'
    return
  }

  if (p.value <= 2 || !isPrime(p.value)) {
    error.value = 'Modül (p) 2\'den büyük tek bir asal sayı olmalıdır.'
    return
  }

  // Euler Kriteri Kullanımı: a^((p-1)/2) mod p
  const exponent = (p.value - 1) / 2
  const modResult = Number(modPow(a.value, exponent, p.value))

  // Eğer sonuç p-1 çıkarsa, bu modüler aritmetikte -1'e denktir
  if (modResult === p.value - 1) {
    result.value = -1
  } else if (modResult === 1) {
    result.value = 1
  } else if (modResult === 0) {
    result.value = 0
  } else {
    error.value = 'Beklenmeyen bir hesaplama hatası oluştu.'
  }
}
</script>

<style scoped>
.calculator {
  margin-top: 24px;
  margin-bottom: 24px;
  padding-bottom: 12px;
  background-color: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
}
.calc-container {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-end;
  padding: 16px 24px;
}
.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.input-group label {
  font-weight: 600;
  font-size: 0.9em;
  color: var(--vp-c-text-1);
}
.input-group input {
  padding: 8px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background-color: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  width: 160px;
  font-family: inherit;
  transition: border-color 0.25s;
}
.input-group input:focus {
  outline: none;
  border-color: var(--vp-c-brand);
}
.calc-button {
  padding: 8px 20px;
  background-color: var(--vp-c-brand);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  height: 40px; /* Inputlar ile aynı hizaya getirir */
  transition: background-color 0.2s;
}
.calc-button:hover {
  background-color: var(--vp-c-brand-hover, #2980b9);
}
.calc-button-reset {
  background-color: var(--vp-c-text-3);
}
.calc-button-reset:hover {
  background-color: var(--vp-c-text-2);
}
.calc-error {
  color: var(--vp-c-danger-1, #e74c3c);
  padding: 0 24px 16px;
  font-weight: 600;
  font-size: 0.9em;
}
.calc-result {
  margin: 8px 24px 24px;
  padding: 16px;
  background-color: var(--vp-c-bg);
  border-left: 4px solid rgb(211, 6, 6);
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.calc-result-success {
  border-left-color: #10b981;
}
.calc-result-danger {
  border-left-color: #ef4444;
}
.calc-result-neutral {
  border-left-color: #8b8b8b;
}
.result-formula {
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: var(--vp-c-text-1);
}
.legendre-symbol {
  display: flex;
  align-items: center;

  font-family: math, serif;
}
.fraction {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0 6px;
}
.numerator {
  border-bottom: 1.5px solid var(--vp-c-text-1);
  padding: 0 4px;
  line-height: 1.2;
}
.denominator {
  line-height: 1.3;
}
.calc-meaning {
  font-size: 0.95em;
  color: var(--vp-c-text-2);
  line-height: 1.5;
}
</style>