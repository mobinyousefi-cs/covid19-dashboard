/*
===========================================================================
Project: COVID-19 Spread Analysis with Flask
File: assets/js/main.js
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-29
Updated: 2025-10-29
License: MIT License (see LICENSE file for details)
===========================================================================
*/
window.addEventListener('DOMContentLoaded', () => {
  // Simple page fade-in
  document.body.style.opacity = 0;
  requestAnimationFrame(() => {
    document.body.style.transition = 'opacity .3s ease';
    document.body.style.opacity = 1;
  });
});