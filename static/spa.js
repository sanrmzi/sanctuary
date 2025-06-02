function loadScriptOnce(src, id) {
  if (document.getElementById(id)) {
    window.dispatchEvent(new Event('spa:content-updated'));
    return;
  }
  const script = document.createElement('script');
  script.src = src;
  script.id = id;
  script.defer = true;
  script.onload = function() {
    window.dispatchEvent(new Event('spa:content-updated'));
  };
  document.body.appendChild(script);
}

document.addEventListener('DOMContentLoaded', function () {
  function ajaxNavigate(url, push=true) {
    fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}})
      .then(res => res.text())
      .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newContent = doc.getElementById('main-content');
        if (newContent) {
          document.getElementById('main-content').innerHTML = newContent.innerHTML;
          if (push) history.pushState({url: url}, '', url);

          // Dynamically load scripts for each page
          if (url.includes('/reminders')) {
            loadScriptOnce('/static/calendar.js', 'calendar-js');
          } else if (url.includes('/todo')) {
            loadScriptOnce('/static/todo.js', 'todo-js');
          } else {
            window.dispatchEvent(new Event('spa:content-updated'));
          }
        }
      });
  }

  document.body.addEventListener('click', function (e) {
    const a = e.target.closest('a.feature, a.recall-btn');
    if (a && a.href && a.target !== '_blank') {
      e.preventDefault();
      ajaxNavigate(a.getAttribute('href'));
    }
  });

  window.addEventListener('popstate', function (e) {
    if (e.state && e.state.url) {
      ajaxNavigate(e.state.url, false);
    }
  });

  // Initial load: if on reminders or todo, load their scripts
  if (window.location.pathname.includes('/reminders')) {
    loadScriptOnce('/static/calendar.js', 'calendar-js');
  } else if (window.location.pathname.includes('/todo')) {
    loadScriptOnce('/static/todo.js', 'todo-js');
  }
});