const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
if (menuButton && navigation) {
  const setMenu = open => {
    navigation.classList.toggle('open', open);
    document.body.classList.toggle('menu-open', open);
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.textContent = open ? 'Fermer' : 'Menu';
  };
  menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && navigation.classList.contains('open')) {
      setMenu(false);
      menuButton.focus();
    }
  });
  navigation.addEventListener('click', event => {
    if (event.target.closest('a')) setMenu(false);
  });
  navigation.addEventListener('focusout', event => {
    if (!navigation.contains(event.relatedTarget) && event.relatedTarget !== menuButton) setMenu(false);
  });
  matchMedia('(min-width: 851px)').addEventListener('change', () => setMenu(false));
}

const photographs = [...document.querySelectorAll('[data-photo]')];
const lightbox = document.querySelector('#lightbox');
if (photographs.length) {
  const filterGroup = document.querySelector('[data-gallery-filters]');
  const filters = [...document.querySelectorAll('[data-filter]')];
  const count = document.querySelector('[data-gallery-count]');
  const notice = document.querySelector('[data-gallery-status]');
  const gallery = document.querySelector('.gallery');
  const canOpen = lightbox && typeof lightbox.showModal === 'function';
  const image = lightbox?.querySelector('img');
  const caption = lightbox?.querySelector('.lightbox-caption');
  const counter = lightbox?.querySelector('[data-counter]');
  const shareLink = lightbox?.querySelector('[data-share-link]');
  const copyButton = lightbox?.querySelector('[data-copy]');
  const copyStatus = lightbox?.querySelector('[data-copy-status]');
  const format = new Intl.NumberFormat('fr-FR');
  let selection = photographs;
  let current = null;
  let opener = null;

  const belongsTo = (link, category) =>
    category === 'toutes' || link.closest('[data-gallery-item]').dataset.categories.split(' ').includes(category);

  const closeViewer = () => {
    if (!lightbox?.open) return;
    const target = opener && !opener.closest('[hidden]') ? opener :
      current && !current.closest('[hidden]') ? current : filters.find(button => button.getAttribute('aria-pressed') === 'true');
    lightbox.close();
    document.body.classList.remove('modal-open');
    target?.focus();
    opener = null;
    current = null;
  };

  const synchronize = () => {
    const url = new URL(location.href);
    let category = filterGroup ? url.searchParams.get('categorie') || 'toutes' : 'toutes';
    const messages = [];
    if (filterGroup && !filters.some(button => button.dataset.filter === category)) {
      category = 'toutes';
      messages.push('Catégorie inconnue : toutes les réalisations sont affichées.');
    }
    if (filterGroup) {
      if (category === 'toutes') url.searchParams.delete('categorie');
      else url.searchParams.set('categorie', category);
    }
    selection = photographs.filter(link => belongsTo(link, category));
    photographs.forEach(link => { link.closest('[data-gallery-item]').hidden = !selection.includes(link); });
    filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === category)));
    gallery?.classList.toggle('is-filtered', category !== 'toutes');
    if (count) {
      const label = filters.find(button => button.dataset.filter === category)?.firstChild.textContent.trim();
      count.textContent = `${format.format(selection.length)} ${selection.length === 1 ? 'photo' : 'photos'} · ${category === 'toutes' ? 'Toutes les réalisations' : label}`;
    }
    const photoId = url.searchParams.get('photo');
    const link = selection.find(photo => photo.dataset.photo === photoId);
    if (photoId && !link) {
      url.searchParams.delete('photo');
      messages.push('Cette photo n’est pas disponible dans cette sélection. Choisissez une autre réalisation.');
    }
    if (url.href !== location.href) history.replaceState(history.state, '', url);
    if (notice) {
      notice.textContent = messages.join(' ');
      notice.hidden = !messages.length;
    }
    if (!link || !canOpen) {
      closeViewer();
      return;
    }
    const changed = current !== link;
    current = link;
    image.src = link.href;
    image.alt = link.querySelector('img').alt;
    image.width = Number(link.dataset.width);
    image.height = Number(link.dataset.height);
    caption.textContent = link.dataset.caption;
    counter.textContent = `${format.format(selection.indexOf(link) + 1)} / ${format.format(selection.length)}`;
    shareLink.href = url.href;
    if (changed) copyStatus.textContent = '';
    if (!lightbox.open) {
      lightbox.showModal();
      document.body.classList.add('modal-open');
    }
  };

  const navigate = (url, replace = false, viewerEntry = false) => {
    history[replace ? 'replaceState' : 'pushState'](
      { ...history.state, proTerPaViewer: viewerEntry }, '', url,
    );
    synchronize();
  };

  const requestClose = () => {
    if (history.state?.proTerPaViewer) {
      history.back();
    } else {
      const url = new URL(location.href);
      url.searchParams.delete('photo');
      navigate(url, true);
    }
  };

  if (filterGroup) {
    filterGroup.hidden = false;
    filters.forEach(button => button.addEventListener('click', () => {
      const url = new URL(location.href);
      if (button.dataset.filter === 'toutes') url.searchParams.delete('categorie');
      else url.searchParams.set('categorie', button.dataset.filter);
      url.searchParams.delete('photo');
      if (url.href !== location.href) navigate(url);
    }));
  }

  if (canOpen) {
    photographs.forEach(link => link.addEventListener('click', event => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
      event.preventDefault();
      opener = link;
      const url = new URL(location.href);
      url.searchParams.set('photo', link.dataset.photo);
      navigate(url, false, true);
    }));
    const move = direction => {
      const index = (selection.indexOf(current) + direction + selection.length) % selection.length;
      const url = new URL(location.href);
      url.searchParams.set('photo', selection[index].dataset.photo);
      navigate(url, true, Boolean(history.state?.proTerPaViewer));
    };
    lightbox.querySelector('[data-close]').addEventListener('click', requestClose);
    lightbox.querySelector('[data-previous]').addEventListener('click', () => move(-1));
    lightbox.querySelector('[data-next]').addEventListener('click', () => move(1));
    lightbox.addEventListener('cancel', event => {
      event.preventDefault();
      requestClose();
    });
    lightbox.addEventListener('keydown', event => {
      if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
        event.preventDefault();
        move(event.key === 'ArrowRight' ? 1 : -1);
      }
    });
    lightbox.addEventListener('click', event => {
      if (event.target === lightbox) requestClose();
    });
    copyButton.addEventListener('click', async () => {
      const copiedURL = location.href;
      const copiedCaption = current.dataset.caption;
      copyButton.disabled = true;
      copyStatus.textContent = 'Copie du lien…';
      try {
        if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(copiedURL);
        copyStatus.textContent = `Lien de « ${copiedCaption} » copié.`;
      } catch {
        copyStatus.textContent = 'Copie impossible dans ce navigateur. Utilisez « Lien de cette photo » pour ouvrir ou copier son adresse.';
      } finally {
        copyButton.disabled = false;
      }
    });
  }
  window.addEventListener('popstate', synchronize);
  synchronize();
}
