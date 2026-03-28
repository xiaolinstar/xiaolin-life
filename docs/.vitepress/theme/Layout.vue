<script setup lang="ts">
import DefaultTheme from 'vitepress/theme'
import MarkdownSourceLink from './components/MarkdownSourceLink.vue'

const { Content } = DefaultTheme
</script>

<template>
  <DefaultTheme.Layout>
    <template #doc-before>
      <MarkdownSourceLink />
    </template>
  </DefaultTheme.Layout>
</template>
