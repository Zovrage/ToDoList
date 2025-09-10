document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('todo-form');
    const titleInput = document.getElementById('todo-input');
    const descInput = document.getElementById('todo-desc');
    const list = document.getElementById('todo-list');

    async function fetchTodos() {
        const response = await fetch('/todos/');
        const todos = await response.json();
        return todos;
    }

    async function renderTodos() {
        const todos = await fetchTodos();
        list.innerHTML = '';
        todos.forEach((todo) => {
            const li = document.createElement('li');
            li.className = 'todo-item' + (todo.completed ? ' completed' : '');

            const titleSpan = document.createElement('span');
            titleSpan.className = 'title';
            titleSpan.textContent = todo.title;
            titleSpan.onclick = async () => {
                todo.completed = !todo.completed;
                await fetch(`/todos/${todo.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ completed: todo.completed })
                });
                renderTodos();
            };

            const descSpan = document.createElement('span');
            descSpan.className = 'description';
            descSpan.textContent = todo.description || '';

            const delBtn = document.createElement('button');
            delBtn.className = 'delete-btn';
            delBtn.textContent = 'Delete';
            delBtn.onclick = async () => {
                await fetch(`/todos/${todo.id}`, { method: 'DELETE' });
                renderTodos();
            };

            li.appendChild(titleSpan);
            li.appendChild(descSpan);
            li.appendChild(delBtn);
            list.appendChild(li);
        });
    }

    form.onsubmit = async (e) => {
        e.preventDefault();
        const title = titleInput.value.trim();
        const description = descInput.value.trim();
        if (!title) return;

        await fetch('/todos/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, completed: false })
        });

        titleInput.value = '';
        descInput.value = '';
        renderTodos();
    };

    renderTodos();
});
