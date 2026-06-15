<script setup>
import { ref } from 'vue'

// Çözümün görünürlük durumunu tutan reaktif değişken
const isSolutionVisible = ref(false)

// Butona tıklandığında görünürlüğü tersine çeviren fonksiyon
const toggleSolution = () => {
  isSolutionVisible.value = !isSolutionVisible.value
}
</script>

<template>
  <div style="border: 1px solid var(--vp-c-divider); border-radius: 8px; padding: 0px 15px 20px 15px; margin: 20px 0; background-color: var(--vp-c-bg-alt);">
    
    <span style="margin-bottom: 15px;">
      <slot name="question"></slot>
    </span>

    <button 
      @click="toggleSolution" 
      style="background-color: var(--vp-c-brand); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 0.9em; transition: opacity 0.2s;"
      onmouseover="this.style.opacity='0.8'"
      onmouseout="this.style.opacity='1'"
    >
      {{ isSolutionVisible ? '🔼 Çözümü Gizle' : '🔽 Çözümü Göster' }}
    </button>

    <div 
      v-show="isSolutionVisible" 
      style="margin-top: 20px; padding-top: 20px; border-top: 1px dashed var(--vp-c-divider);"
    >
      <slot name="solution"></slot>
    </div>
    
  </div>
</template>