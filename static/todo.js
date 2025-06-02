document.addEventListener('DOMContentLoaded', function () {
  // Toggle done/undone via AJAX
  document.querySelectorAll('.task-label').forEach(function (label) {
    label.addEventListener('click', function () {
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
  });

  // Edit modal logic
  window.editTask = function (taskId, taskText) {
    document.getElementById('edit-modal').style.display = 'flex';
    document.getElementById('edit-task-input').value = taskText;
    const form = document.getElementById('edit-task-form');
    form.onsubmit = function (e) {
      e.preventDefault();
      fetch(`/edit_task_ajax/${taskId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: document.getElementById('edit-task-input').value })
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            document.querySelector(`li[data-task-id="${taskId}"] .task-label`).textContent = data.task;
            closeEditModal();
          }
        });
    };
  };
  window.closeEditModal = function () {
    document.getElementById('edit-modal').style.display = 'none';
  };
});