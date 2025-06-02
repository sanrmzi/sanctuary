document.addEventListener('DOMContentLoaded', function () {
  let currentMonth = new Date().getMonth();
  let currentYear = new Date().getFullYear();
  let reminders = window.remindersData || {};

  function fetchReminders(year, month) {
    fetch(`/reminders_data?year=${year}&month=${month + 1}`)
      .then(res => res.json())
      .then(data => {
        reminders = data;
        renderCalendar(year, month);
      });
  }

  function renderCalendar(year, month) {
    const calendar = document.getElementById('calendar');
    calendar.innerHTML = '';
    const monthYear = document.getElementById('calendar-month-year');
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const today = new Date();
    monthYear.textContent = `${new Date(year, month).toLocaleString('default', { month: 'long' })} ${year}`;

    // Weekday headers
    const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    weekdays.forEach(day => {
      const header = document.createElement('div');
      header.textContent = day;
      header.style.fontWeight = 'bold';
      header.style.textAlign = 'center';
      calendar.appendChild(header);
    });

    // Empty slots before first day
    for (let i = 0; i < firstDay; i++) {
      const empty = document.createElement('div');
      calendar.appendChild(empty);
    }

    // Days
    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      const cell = document.createElement('div');
      cell.className = 'calendar-day';
      if (
        day === today.getDate() &&
        month === today.getMonth() &&
        year === today.getFullYear()
      ) {
        cell.classList.add('today');
      }
      cell.setAttribute('data-date', dateStr);

      // Day number
      const num = document.createElement('div');
      num.className = 'day-number';
      num.textContent = day;
      cell.appendChild(num);

      // Reminders
      if (reminders[dateStr]) {
        const rList = document.createElement('div');
        rList.className = 'reminder-list';
        reminders[dateStr].forEach(rem => {
          const item = document.createElement('div');
          item.className = 'reminder-item';
          item.setAttribute('data-reminder-id', rem.id);
          item.ondblclick = function (e) {
            e.stopPropagation();
            openReminderModal(dateStr, rem);
          };
          // Show up to 12 letters for the title
          let shortTitle = rem.title.length > 12 ? rem.title.slice(0, 12) + '…' : rem.title;
          item.innerHTML = `<span class="reminder-dot" style="background:${rem.color};"></span>${rem.time ? `<span style="color:#5c6a82;font-size:0.95em;margin-right:4px;">${rem.time}</span>` : ''}<strong>${shortTitle}</strong>`;
          if (rem.done) item.style.opacity = "0.5";
          rList.appendChild(item);
        });
        cell.appendChild(rList);
      }

      // Double click to add new reminder
      cell.ondblclick = function (e) {
        if (e.target === cell) openReminderModal(dateStr, null);
      };

      calendar.appendChild(cell);
    }
  }

  function openReminderModal(dateStr, reminder) {
    document.getElementById('reminder-modal').style.display = 'flex';
    document.getElementById('modal-date').textContent = dateStr;
    document.getElementById('reminder-form').reset();
    document.getElementById('reminder-form').setAttribute('data-date', dateStr);

    // Hide all action buttons by default
    document.getElementById('delete-reminder-btn').style.display = 'none';
    document.getElementById('done-reminder-btn').style.display = 'none';
    document.getElementById('undone-reminder-btn').style.display = 'none';
    document.getElementById('reminder-id').value = '';

    if (reminder) {
      document.getElementById('reminder-title').value = reminder.title;
      document.getElementById('reminder-desc').value = reminder.description;
      document.getElementById('reminder-time').value = reminder.time || '';
      document.getElementById('reminder-color').value = reminder.color || '#5c6a82';
      document.getElementById('reminder-id').value = reminder.id;
      document.getElementById('delete-reminder-btn').style.display = '';
      if (reminder.done) {
        document.getElementById('undone-reminder-btn').style.display = '';
      } else {
        document.getElementById('done-reminder-btn').style.display = '';
      }
    }
  }
  window.closeReminderModal = function () {
    document.getElementById('reminder-modal').style.display = 'none';
  };

  document.getElementById('reminder-form').onsubmit = function (e) {
    e.preventDefault();
    const date = this.getAttribute('data-date');
    const id = document.getElementById('reminder-id').value;
    const title = document.getElementById('reminder-title').value;
    const description = document.getElementById('reminder-desc').value;
    const time = document.getElementById('reminder-time').value;
    const color = document.getElementById('reminder-color').value;
    const url = id ? '/edit_reminder' : '/add_reminder';
    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, date, title, description, time, color })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          closeReminderModal();
          fetchReminders(currentYear, currentMonth);
        }
      });
  };

  document.getElementById('delete-reminder-btn').onclick = function () {
    const id = document.getElementById('reminder-id').value;
    if (!id) return;
    fetch('/delete_reminder', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          closeReminderModal();
          fetchReminders(currentYear, currentMonth);
        }
      });
  };

  document.getElementById('done-reminder-btn').onclick = function () {
    const id = document.getElementById('reminder-id').value;
    if (!id) return;
    fetch('/done_reminder', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          closeReminderModal();
          fetchReminders(currentYear, currentMonth);
        }
      });
  };

  document.getElementById('undone-reminder-btn').onclick = function () {
    const id = document.getElementById('reminder-id').value;
    if (!id) return;
    fetch('/undone_reminder', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          closeReminderModal();
          fetchReminders(currentYear, currentMonth);
        }
      });
  };

  document.getElementById('prev-month').onclick = function () {
    currentMonth--;
    if (currentMonth < 0) {
      currentMonth = 11;
      currentYear--;
    }
    fetchReminders(currentYear, currentMonth);
  };
  document.getElementById('next-month').onclick = function () {
    currentMonth++;
    if (currentMonth > 11) {
      currentMonth = 0;
      currentYear++;
    }
    fetchReminders(currentYear, currentMonth);
  };

  // Initial load
  fetchReminders(currentYear, currentMonth);
});