<script setup>
import { Check } from 'lucide-vue-next'
import { useToast } from '../composables/useToast'

const { toast } = useToast()
</script>

<template>
  <Transition>
    <div v-if="toast" class="toast"><Check :size="14" />{{ toast }}</div>
  </Transition>
</template>
