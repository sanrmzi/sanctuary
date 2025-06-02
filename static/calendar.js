const remindersCache = {};

function initCalendarPage() {
  const calendar = document.getElementById('calendar');
  if (!calendar) return;

  // State: keep month/year across SPA navigation
  let calendarState = window.__calendarState || {
    currentMonth: new Date().getMonth(),
    currentYear: new Date().getFullYear()
  };

  function fetchReminders(year, month, force = false) {
    const cacheKey = `${year}-${month}`;
    if (!force && remindersCache[cacheKey]) {
      renderCalendar(year, month, remindersCache[cacheKey]);
      return;
    }
    fetch(`/reminders_data?year=${year}&month=${month + 1}`)
      .then(res => res.json())
      .then(data => {
        remindersCache[cacheKey] = data;
        renderCalendar(year, month, data);
      });
  }

  function renderCalendar(year, month, reminders) {
    calendar.innerHTML = '';
    const monthYear = document.getElementById('calendar-month-year');
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const today = new Date();
    monthYear.textContent = `${new Date(year, month).toLocaleString('default', { month: 'long' })} ${year}`;

    // Weekdays
    ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].forEach(day => {
      const header = document.createElement('div');
      header.textContent = day;
      header.style.fontWeight = 'bold';
      header.style.textAlign = 'center';
      calendar.appendChild(header);
    });

    // Empty slots
    for (let i = 0; i < firstDay; i++) {
      calendar.appendChild(document.createElement('div'));
    }

    // Days
    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${year}-${String(month+1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
      const cell = document.createElement('div');
      cell.className = 'calendar-day';
      if (day === today.getDate() && month === today.getMonth() && year === today.getFullYear()) {
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
          let shortTitle = rem.title.length > 12 ? rem.title.slice(0, 12) + '…' : rem.title;
          item.innerHTML = `<span class="reminder-dot" style="background:${rem.color};"></span><strong>${shortTitle}</strong>`;
          if (rem.done) item.style.opacity = "0.5";
          // Double click to edit
          item.ondblclick = function(e) {
            e.stopPropagation();
            openReminderModal(dateStr, rem);
          };
          rList.appendChild(item);
        });
        cell.appendChild(rList);
      }

      // Double click to add new reminder
      cell.ondblclick = function(e) {
        if (e.target === cell) openReminderModal(dateStr, null);
      };

      calendar.appendChild(cell);
    }
  }

  // Modal logic
  window.closeReminderModal = function () {
    document.getElementById('reminder-modal').style.display = 'none';
  };

  function openReminderModal(dateStr, reminder) {
    document.getElementById('reminder-modal').style.display = 'flex';
    document.getElementById('modal-date').textContent = dateStr;
    document.getElementById('reminder-form').reset();
    document.getElementById('reminder-form').setAttribute('data-date', dateStr);

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

  const reminderForm = document.getElementById('reminder-form');
  if (reminderForm) {
    reminderForm.onsubmit = function (e) {
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
            const cacheKey = `${calendarState.currentYear}-${calendarState.currentMonth}`;
            delete remindersCache[cacheKey];
            fetchReminders(calendarState.currentYear, calendarState.currentMonth, true);
          }
        });
    };
  }

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
          const cacheKey = `${calendarState.currentYear}-${calendarState.currentMonth}`;
          delete remindersCache[cacheKey];
          fetchReminders(calendarState.currentYear, calendarState.currentMonth, true);
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
          const cacheKey = `${calendarState.currentYear}-${calendarState.currentMonth}`;
          delete remindersCache[cacheKey];
          fetchReminders(calendarState.currentYear, calendarState.currentMonth, true);
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
          const cacheKey = `${calendarState.currentYear}-${calendarState.currentMonth}`;
          delete remindersCache[cacheKey];
          fetchReminders(calendarState.currentYear, calendarState.currentMonth, true);
        }
      });
  };

  document.getElementById('prev-month').onclick = function () {
    calendarState.currentMonth--;
    if (calendarState.currentMonth < 0) {
      calendarState.currentMonth = 11;
      calendarState.currentYear--;
    }
    fetchReminders(calendarState.currentYear, calendarState.currentMonth);
  };
  document.getElementById('next-month').onclick = function () {
    calendarState.currentMonth++;
    if (calendarState.currentMonth > 11) {
      calendarState.currentMonth = 0;
      calendarState.currentYear++;
    }
    fetchReminders(calendarState.currentYear, calendarState.currentMonth);
  };

  // Save state globally for SPA navigation
  window.__calendarState = calendarState;

  // Initial load
  fetchReminders(calendarState.currentYear, calendarState.currentMonth);
}

// Always re-initialize on SPA content update
window.addEventListener('spa:content-updated', function () {
  if (document.getElementById('calendar')) {
    initCalendarPage();
  }
});

// Also run on first load
document.addEventListener('DOMContentLoaded', function () {
  if (document.getElementById('calendar')) {
    initCalendarPage();
  }
});

function updateDayCell(year, month, dateStr, remindersForDay) {
  const cell = document.querySelector(`.calendar-day[data-date="${dateStr}"]`);
  if (!cell) return;
  // Remove old reminders list
  const oldList = cell.querySelector('.reminder-list');
  if (oldList) cell.removeChild(oldList);

  // Add new reminders list
  if (remindersForDay && remindersForDay.length) {
    const rList = document.createElement('div');
    rList.className = 'reminder-list';
    remindersForDay.forEach(rem => {
      const item = document.createElement('div');
      item.className = 'reminder-item';
      let shortTitle = rem.title.length > 12 ? rem.title.slice(0, 12) + '…' : rem.title;
      item.innerHTML = `<span class="reminder-dot" style="background:${rem.color};"></span><strong>${shortTitle}</strong>`;
      if (rem.done) item.style.opacity = "0.5";
      item.ondblclick = function(e) {
        e.stopPropagation();
        openReminderModal(dateStr, rem);
      };
      rList.appendChild(item);
    });
    cell.appendChild(rList);
  }
}