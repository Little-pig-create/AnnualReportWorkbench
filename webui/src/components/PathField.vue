<template>
  <label class="field">
    <span>{{ label }}</span>
    <div class="input-row">
      <input :value="modelValue" @input="onInput" @blur="$emit('blur')" :placeholder="placeholder" />
      <div class="actions">
        <button v-if="selectable" type="button" class="secondary" @click="$emit('select')">选择</button>
        <button v-if="openable" type="button" @click="$emit('open')">打开</button>
      </div>
    </div>
  </label>
</template>

<script setup lang="ts">
defineProps<{
  label: string;
  modelValue: string;
  placeholder?: string;
  openable?: boolean;
  selectable?: boolean;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: string];
  open: [];
  select: [];
  blur: [];
}>();

function onInput(event: Event) {
  emit("update:modelValue", (event.target as HTMLInputElement).value);
}
</script>

<style scoped>
.field {
  display: grid;
  gap: 8px;
}

.field span {
  font-size: var(--type-body-small);
  color: var(--muted);
}

.input-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: center;
}

input {
  width: 100%;
  min-height: var(--control-height-sm);
  padding: 8px 11px;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--field-bg);
  color: var(--field-text);
}

input::placeholder {
  color: var(--field-placeholder);
}

.actions {
  display: flex;
  gap: 6px;
  align-items: center;
}

button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--surface-strong);
  color: var(--text);
  min-height: var(--control-height-sm);
  min-width: 64px;
  padding: 0 12px;
  cursor: pointer;
  font-size: var(--type-body-small);
  box-shadow: none;
}

.secondary {
  background: var(--surface-strong);
  color: var(--text);
}
</style>
