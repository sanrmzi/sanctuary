function initTodoPage() {
  // Attach double-click to toggle done for existing tasks
  document.querySelectorAll('.task-label').forEach(function (label) {
    if (!label.dataset.dblAttached) {
      label.addEventListener('dblclick', function () {
        const li = label.closest('.task-item');
        const taskId = li.getAttribute('data-task-id');
        fetch(`/toggle_task_ajax/${taskId}`, { method: 'POST' })
          .then(res => res.json())
          .then(data => {
            if (data.success) {
              li.classList.toggle('task-done', data.done);
            }
          });
      });
      label.dataset.dblAttached = "1";
    }
  });

  // Attach delete handler for existing tasks
  document.querySelectorAll('.delete-task-form').forEach(function (form) {
    if (!form.dataset.deleteAttached) {
      form.onsubmit = function (e) {
        e.preventDefault();
        fetch(form.action, { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' } })
          .then(res => res.json())
          .then(data => {
            if (data.success) {
              const li = form.closest('li.task-item');
              if (li) li.remove();
            }
          });
      };
      form.dataset.deleteAttached = "1";
    }
  });

  // Edit modal logic
  window.editTask = function (taskId, taskTitle) {
    const modal = document.getElementById('edit-modal');
    if (!modal) {
      alert('Edit modal not found in DOM!');
      return;
    }
    modal.style.display = 'flex';
    document.getElementById('edit-task-input').value = taskTitle;
    const form = document.getElementById('edit-task-form');
    form.onsubmit = null; // Remove previous handler
    form.onsubmit = function (e) {
      e.preventDefault();
      fetch(`/edit_task_ajax/${taskId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: document.getElementById('edit-task-input').value })
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            document.querySelector(`li[data-task-id="${taskId}"] .task-label`).textContent = data.title;
            closeEditModal();
          }
        });
    };
  };
  window.closeEditModal = function () {
    document.getElementById('edit-modal').style.display = 'none';
  };

  // Add task via AJAX and update DOM directly
  const addForm = document.getElementById('add-task-form');
  if (addForm) {
    addForm.onsubmit = function (e) {
      e.preventDefault();
      const input = document.getElementById('task');
      const task = input.value.trim();
      if (!task) return;
      fetch('/add_task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' },
        body: `task=${encodeURIComponent(task)}`
      })
        .then(res => res.json())
        .then(data => {
          if (data.success && data.html) {
            document.getElementById('task-list').outerHTML = data.html;
            input.value = '';
            initTodoPage(); // re-attach handlers
          }
        });
    };
  }

  document.querySelectorAll('.task-action-btn.edit').forEach(function(btn) {
    btn.onclick = function() {
      editTask(
        btn.getAttribute('data-task-id'),
        btn.getAttribute('data-task-text')
      );
    };
  });

  const resetForm = document.getElementById('reset-tasks-form');
  if (resetForm) {
    resetForm.onsubmit = function(e) {
      e.preventDefault();
      fetch(resetForm.action, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
        .then(res => res.text())
        .then(html => {
          document.getElementById('task-list').outerHTML = html;
          initTodoPage();
        });
    };
  }
}

// Run on initial load
document.addEventListener('DOMContentLoaded', function () {
  if (document.getElementById('task-list')) {
    initTodoPage();
  }
  console.log('edit-modal exists:', !!document.getElementById('edit-modal'));
});

// Run after SPA navigation
window.addEventListener('spa:content-updated', function () {
  if (document.getElementById('task-list')) {
    initTodoPage();
  }
});