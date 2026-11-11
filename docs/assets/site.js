const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
if (menuButton && navigation) {
  const closeMenu = () => {
    navigation.classList.remove('open');
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.textContent = 'Menu';
  };
  menuButton.addEventListener('click', () => {
    const open = menuButton.getAttribute('aria-expanded') !== 'true';
    navigation.classList.toggle('open', open);
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.textContent = open ? 'Fermer' : 'Menu';
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && navigation.classList.contains('open')) {
      closeMenu();
      menuButton.focus();
    }
  });
  navigation.addEventListener('click', event => {
    if (event.target.closest('a')) closeMenu();
  });
  navigation.addEventListener('focusout', event => {
    if (!navigation.contains(event.relatedTarget) && event.relatedTarget !== menuButton) closeMenu();
  });
}

const photographs = [...document.querySelectorAll('[data-photo]')];
const lightbox = document.querySelector('#lightbox');
if (photographs.length && lightbox && typeof lightbox.showModal === 'function') {
  const image = lightbox.querySelector('img');
  const caption = lightbox.querySelector('.lightbox-caption');
  const counter = lightbox.querySelector('[data-counter]');
  let current = 0;
  let opener = null;
  const display = index => {
    current = (index + photographs.length) % photographs.length;
    const link = photographs[current];
    image.src = link.href;
    image.alt = link.querySelector('img').alt;
    caption.textContent = link.dataset.caption || image.alt;
    counter.textContent = `${current + 1} / ${photographs.length}`;
  };
  photographs.forEach((link, index) => {
    link.addEventListener('click', event => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      opener = link;
      display(index);
      lightbox.showModal();
      document.body.style.overflow = 'hidden';
    });
  });
  lightbox.querySelector('[data-close]').addEventListener('click', () => lightbox.close());
  lightbox.querySelector('[data-previous]').addEventListener('click', () => display(current - 1));
  lightbox.querySelector('[data-next]').addEventListener('click', () => display(current + 1));
  lightbox.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      display(current + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
  lightbox.addEventListener('click', event => {
    if (event.target === lightbox) lightbox.close();
  });
  lightbox.addEventListener('close', () => {
    document.body.style.overflow = '';
    opener?.focus();
  });
}
