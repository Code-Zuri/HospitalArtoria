/* ============================================================
   HOSPITAL ARTORIA — app.js
   Script puramente de presentación: no interviene en la lógica
   de las rutas Flask ni en los fetch/formularios existentes.
   Se limita a:
     1) Resaltar el ítem activo del navbar según la URL actual.
     2) Mostrar una barra de carga minimalista al navegar.
     3) Animar la entrada del contenido con anime.js.
     4) Autodesvanecer los mensajes flash.
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) lucide.createIcons();

  /* ---------- 1) Navbar activo según la ruta actual ---------- */
  const currentPath = window.location.pathname.replace(/\/+$/, '') || '/';
  document.querySelectorAll('.nav-item[href]').forEach((item) => {
    const href = item.getAttribute('href').replace(/\/+$/, '') || '/';
    if (href === currentPath) {
      item.classList.add('active');
    }
  });

  /* ---------- 2) Barra de carga al navegar entre páginas ---------- */
  const loadingBar = document.getElementById('loadingBar');
  if (loadingBar && window.anime) {
    document.querySelectorAll('a.nav-item[href], .sidebar a[href]').forEach((link) => {
      link.addEventListener('click', (e) => {
        const url = link.getAttribute('href');
        if (!url || url.startsWith('#') || link.target === '_blank') return;
        e.preventDefault();
        anime.remove(loadingBar);
        loadingBar.style.opacity = 1;
        loadingBar.style.width = '0%';
        anime({ targets: loadingBar, width: ['0%', '75%'], duration: 320, easing: 'easeOutQuad' });
        setTimeout(() => { window.location.href = url; }, 260);
      });
    });
  }
  if (loadingBar && window.anime) {
    anime({ targets: loadingBar, width: '100%', duration: 200, easing: 'easeOutQuad', complete: () => {
      anime({ targets: loadingBar, opacity: 0, duration: 220, delay: 100, easing: 'easeOutQuad' });
    }});
  }

  /* ---------- 3) Animación de entrada del contenido ---------- */
  if (window.anime) {
    const target = document.querySelector('.container') || document.body;
    anime({
      targets: target,
      opacity: [0, 1],
      translateY: [8, 0],
      duration: 420,
      easing: 'easeOutCubic'
    });

    anime({
      targets: '.container > *',
      opacity: [0, 1],
      translateY: [10, 0],
      delay: anime.stagger(45),
      duration: 380,
      easing: 'easeOutCubic'
    });

    anime({
      targets: '.nav-item',
      opacity: [0, 1],
      translateX: [-6, 0],
      delay: anime.stagger(20),
      duration: 320,
      easing: 'easeOutCubic'
    });
  }

  /* ---------- 4) Autodesvanecer mensajes flash ---------- */
  const flashes = document.querySelectorAll('[class^="flash-"]');
  if (flashes.length && window.anime) {
    setTimeout(() => {
      anime({
        targets: flashes,
        opacity: [1, 0],
        translateY: [0, -6],
        duration: 320,
        easing: 'easeInCubic',
        delay: anime.stagger(60),
        complete: () => flashes.forEach((f) => f.style.display = 'none')
      });
    }, 4200);
  }
});
