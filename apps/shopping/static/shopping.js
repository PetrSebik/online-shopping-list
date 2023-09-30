function addItem(event) {
    event.preventDefault();
    let itemNameInput = document.getElementById('item-value');
    let itemName = itemNameInput.value;

    let itemData = {name: itemName};

    fetch('/shopping/item/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(itemData)
    })
        .then(response => response.json())
        .then(data => {
            updateList(data)
            itemNameInput.value = '';
        })
        .catch(error => {
            console.error('Error:', error);
        });
    return false;
}

function fetchItems() {
    fetch('/shopping/items/list/')
        .then(response => response.json())
        .then(data => {
            data.forEach(item => {
                updateList(item);
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function updateList(item) {
    let itemId = `item-${item.id}`;

    let listItem = document.getElementById(itemId);

    if (!listItem) {
        // create the <li> element
        listItem = document.createElement('li');
        listItem.id = itemId;
        listItem.className = 'list-group-item';

        if (item.quantity !== null) {
            listItem.textContent = `${item.quantity}x ${item.name}`;
        } else {
            listItem.textContent = item.name;
        }

        // crete the <a> element for deleting the item
        let removeLink = document.createElement('a');
        removeLink.id = `remove-${item.id}`;
        removeLink.className = 'btn btn-danger btn-sm float-end';
        removeLink.addEventListener('click', () => {
            removeItem(item.id);
        });

        // add icon the <a> element delete button
        let iconElement = document.createElement('i');
        iconElement.className = 'bi bi-x-lg';
        removeLink.appendChild(iconElement);
        listItem.appendChild(removeLink);

        // add the <li> element to the <ul> element
        let listContainer = document.getElementById('list-items');
        listContainer.appendChild(listItem);
    }
}

function removeItem(itemId) {
    fetch(`/shopping/item/${itemId}/`, {
        method: 'DELETE',
    })
        .then(response => {
            if (response.ok) {
                let listItem = document.getElementById(`item-${itemId}`);
                if (listItem) {
                    listItem.remove();
                }
            } else {
                console.error('Failed to delete item:', response.status);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

document.addEventListener('DOMContentLoaded', () => {
    let button = document.getElementById('add-btn');

    button.addEventListener('click', addItem);

    document.querySelectorAll('[id^="remove-"]').forEach(removeLink => {
        let itemId = removeLink.id.replace('remove-', '');

        removeLink.addEventListener('click', () => {
            removeItem(itemId);
        });
    });

    // fetch new items every 10 sec
    setInterval(fetchItems, 10 * 1000);
})
