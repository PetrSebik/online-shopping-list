let displayedItemIds = [];

function initializeDisplayedItemIds() {
    let listItems = document.querySelectorAll('[id^="item-"]');
    listItems.forEach(item => {
        // Extract the item ID from the ID attribute
        let itemId = parseInt(item.id.replace('item-', ''), 10);
        if (!isNaN(itemId)) {
            displayedItemIds.push(itemId);
        }
    });
}

function addItem(event) {
    event.preventDefault();
    let itemNameInput = document.getElementById('item-value');
    let itemName = itemNameInput.value;

    let itemData = {name: itemName};
    let csrfTokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');

    fetch('/shopping/item/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            "X-CSRFToken": csrfTokenInput.value
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

    focusInput();
    return false;
}

function fetchItems() {
    fetch('/shopping/items/list/')
        .then(response => response.json())
        .then(data => {
            let fetchedItemIds = data.map(item => item.id);
            let removedItemIds = displayedItemIds.filter(id => !fetchedItemIds.includes(id));

            removedItemIds.forEach(id => {
                let listItem = document.getElementById(`item-${id}`);
                if (listItem) {
                    listItem.remove();
                }
                displayedItemIds = displayedItemIds.filter(item => item !== id);
            });

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
        displayedItemIds.push(item.id);
    }
}

function removeItem(itemId) {
    let csrfTokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    fetch(`/shopping/item/${itemId}/`, {
        method: 'DELETE',
        headers: {
            "X-CSRFToken": csrfTokenInput.value
        },
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

function focusInput() {
    let itemValueInput = document.getElementById('item-value');
    itemValueInput.focus();
}

document.addEventListener('DOMContentLoaded', () => {
    let button = document.getElementById('add-btn');

    focusInput();

    button.addEventListener('click', addItem);

    initializeDisplayedItemIds();

    document.querySelectorAll('[id^="remove-"]').forEach(removeLink => {
        let itemId = removeLink.id.replace('remove-', '');

        removeLink.addEventListener('click', () => {
            removeItem(itemId);
        });
    });

    // fetch new items every 10 sec
    setInterval(fetchItems, 10 * 1000);
})
