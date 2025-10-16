// Advanced Drag & Drop Interface Engine
// Based on the transcript demonstration patterns

class DragDropEngine {
    constructor(floorPlanEngine) {
        this.floorPlan = floorPlanEngine;
        this.isDragging = false;
        this.draggedElement = null;
        this.dragMode = null; // 'people', 'equipment', 'category'
        this.activePersonList = [];
        this.dragPreview = null;

        this.init();
    }

    init() {
        this.setupPeopleDragDrop();
        this.setupEquipmentDragDrop();
        this.createDragPreview();
    }

    createDragPreview() {
        this.dragPreview = document.createElement('div');
        this.dragPreview.id = 'drag-preview';
        this.dragPreview.style.cssText = `
            position: fixed;
            pointer-events: none;
            background: rgba(25, 118, 210, 0.9);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            z-index: 9999;
            opacity: 0;
            transition: opacity 0.2s;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;
        document.body.appendChild(this.dragPreview);
    }

    showDragPreview(x, y, text) {
        this.dragPreview.textContent = text;
        this.dragPreview.style.left = (x + 15) + 'px';
        this.dragPreview.style.top = (y - 10) + 'px';
        this.dragPreview.style.opacity = '1';
    }

    hideDragPreview() {
        this.dragPreview.style.opacity = '0';
    }

    setupPeopleDragDrop() {
        // Create people assignment interface exactly like the transcript
        this.createPeopleAssignmentUI();
    }

    createPeopleAssignmentUI() {
        // Enhanced people modal with drag-and-drop functionality
        const existingModal = document.getElementById('people-modal');
        if (existingModal) {
            existingModal.remove();
        }

        const modal = document.createElement('div');
        modal.id = 'people-modal';
        modal.style.cssText = `
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            align-items: flex-start;
            justify-content: flex-end;
            padding: 20px;
        `;

        modal.innerHTML = `
            <div style="background: white; border-radius: 12px; padding: 0; max-width: 400px; width: 100%; max-height: 80vh; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #1976d2, #42a5f5); color: white; padding: 20px; text-align: center;">
                    <h3 style="margin: 0; font-size: 18px; font-weight: 600;">Assign People to Spaces</h3>
                    <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 14px;">Drag people to assign them to selected spaces</p>
                </div>

                <!-- Filter Controls -->
                <div style="padding: 15px; border-bottom: 1px solid #e0e0e0; background: #f8f9fa;">
                    <div style="margin-bottom: 10px;">
                        <label style="font-size: 12px; color: #666; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Filter by Type:</label>
                    </div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <button class="filter-btn active" data-filter="all" style="padding: 6px 12px; border: 1px solid #d0d0d0; border-radius: 16px; background: #1976d2; color: white; font-size: 12px; cursor: pointer;">All</button>
                        <button class="filter-btn" data-filter="internal" style="padding: 6px 12px; border: 1px solid #d0d0d0; border-radius: 16px; background: white; color: #666; font-size: 12px; cursor: pointer;">Internal</button>
                        <button class="filter-btn" data-filter="contractor" style="padding: 6px 12px; border: 1px solid #d0d0d0; border-radius: 16px; background: white; color: #666; font-size: 12px; cursor: pointer;">Contractors</button>
                        <button class="filter-btn" data-filter="unassigned" style="padding: 6px 12px; border: 1px solid #d0d0d0; border-radius: 16px; background: white; color: #666; font-size: 12px; cursor: pointer;">No Seating</button>
                    </div>
                </div>

                <!-- People List -->
                <div id="people-list" style="max-height: 400px; overflow-y: auto; padding: 15px;">
                    <!-- Will be populated dynamically -->
                </div>

                <!-- Actions -->
                <div style="padding: 15px; border-top: 1px solid #e0e0e0; display: flex; gap: 10px; justify-content: flex-end;">
                    <button id="cancel-assignment" style="padding: 10px 20px; background: #f5f5f5; border: 1px solid #d0d0d0; border-radius: 6px; cursor: pointer; font-weight: 500;">Cancel</button>
                    <button id="bulk-assign" style="padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;">Bulk Assign</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Setup filter functionality
        modal.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                modal.querySelectorAll('.filter-btn').forEach(b => {
                    b.style.background = 'white';
                    b.style.color = '#666';
                });
                e.target.style.background = '#1976d2';
                e.target.style.color = 'white';
                this.filterPeople(e.target.dataset.filter);
            });
        });

        // Setup modal controls
        modal.querySelector('#cancel-assignment').onclick = () => {
            this.closePeopleModal();
        };

        modal.querySelector('#bulk-assign').onclick = () => {
            this.performBulkAssignment();
        };

        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closePeopleModal();
            }
        });
    }

    openPeopleModal() {
        if (this.floorPlan.selectedSpaces.length === 0) {
            this.showNotification('Please select one or more spaces first', 'warning');
            return;
        }

        const modal = document.getElementById('people-modal');
        modal.style.display = 'flex';
        this.loadPeopleList();
        this.setupSpaceDropZones();
    }

    closePeopleModal() {
        const modal = document.getElementById('people-modal');
        modal.style.display = 'none';
    }

    loadPeopleList() {
        // Sample people data (would come from backend in real app)
        const samplePeople = [
            { id: 1, name: 'Danny Ocean', type: 'contractor', status: 'active', hasSeating: false, department: 'Security', avatar: 'DO' },
            { id: 2, name: 'Linus Caldwell', type: 'contractor', status: 'active', hasSeating: false, department: 'IT', avatar: 'LC' },
            { id: 3, name: 'Frank Catton', type: 'contractor', status: 'active', hasSeating: false, department: 'Facilities', avatar: 'FC' },
            { id: 4, name: 'Vaughn Jones', type: 'internal', status: 'active', hasSeating: true, department: 'Management', avatar: 'VJ' },
            { id: 5, name: 'Bill Roberts', type: 'internal', status: 'active', hasSeating: false, department: 'Operations', avatar: 'BR' },
            { id: 6, name: 'Sarah Chen', type: 'internal', status: 'active', hasSeating: false, department: 'Engineering', avatar: 'SC' },
            { id: 7, name: 'Mike Torres', type: 'contractor', status: 'active', hasSeating: false, department: 'Maintenance', avatar: 'MT' }
        ];

        this.activePersonList = samplePeople;
        this.renderPeopleList(samplePeople);
    }

    renderPeopleList(people) {
        const peopleList = document.getElementById('people-list');
        peopleList.innerHTML = '';

        people.forEach(person => {
            const personItem = document.createElement('div');
            personItem.className = 'person-item';
            personItem.draggable = true;
            personItem.dataset.personId = person.id;

            personItem.style.cssText = `
                display: flex;
                align-items: center;
                padding: 12px;
                margin-bottom: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                cursor: grab;
                transition: all 0.2s;
                background: white;
            `;

            personItem.innerHTML = `
                <div style="
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #1976d2, #42a5f5);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    margin-right: 12px;
                    font-size: 14px;
                ">${person.avatar}</div>

                <div style="flex: 1;">
                    <div style="font-weight: 600; font-size: 14px; color: #333; margin-bottom: 2px;">${person.name}</div>
                    <div style="font-size: 12px; color: #666;">
                        ${person.department} • ${person.type}
                        ${!person.hasSeating ? ' • <span style="color: #f44336;">No Seating</span>' : ''}
                    </div>
                </div>

                <div style="display: flex; align-items: center; gap: 8px;">
                    <button class="assign-btn" data-person-id="${person.id}" style="
                        padding: 6px 12px;
                        background: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 11px;
                        font-weight: 500;
                    ">Assign</button>
                </div>
            `;

            // Add drag functionality
            this.setupPersonDrag(personItem, person);

            // Add click assignment
            personItem.querySelector('.assign-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                this.assignPersonToSelectedSpaces(person);
            });

            peopleList.appendChild(personItem);
        });
    }

    setupPersonDrag(personItem, person) {
        personItem.addEventListener('dragstart', (e) => {
            this.isDragging = true;
            this.draggedElement = person;
            this.dragMode = 'people';

            personItem.style.opacity = '0.5';
            personItem.style.cursor = 'grabbing';

            // Create drag data
            e.dataTransfer.setData('text/plain', JSON.stringify(person));
            e.dataTransfer.effectAllowed = 'move';

            this.showDragPreview(e.clientX, e.clientY, `Assigning: ${person.name}`);
        });

        personItem.addEventListener('dragend', (e) => {
            this.isDragging = false;
            this.draggedElement = null;
            personItem.style.opacity = '1';
            personItem.style.cursor = 'grab';
            this.hideDragPreview();
        });

        // Hover effects
        personItem.addEventListener('mouseenter', () => {
            if (!this.isDragging) {
                personItem.style.borderColor = '#1976d2';
                personItem.style.boxShadow = '0 2px 8px rgba(25, 118, 210, 0.2)';
            }
        });

        personItem.addEventListener('mouseleave', () => {
            if (!this.isDragging) {
                personItem.style.borderColor = '#e0e0e0';
                personItem.style.boxShadow = 'none';
            }
        });
    }

    setupSpaceDropZones() {
        // Make spaces droppable
        document.querySelectorAll('.space').forEach(space => {
            space.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';

                // Highlight drop zone
                space.style.fill = '#e3f2fd';
                space.style.stroke = '#1976d2';
                space.style.strokeWidth = '3';
            });

            space.addEventListener('dragleave', () => {
                // Remove highlight
                this.floorPlan.updateViewDisplay();
            });

            space.addEventListener('drop', (e) => {
                e.preventDefault();
                const personData = JSON.parse(e.dataTransfer.getData('text/plain'));

                // Remove highlight
                this.floorPlan.updateViewDisplay();

                // Perform assignment
                this.assignPersonToSpace(personData, space);

                this.showNotification(`Assigned ${personData.name} to space ${space.id}`, 'success');
            });
        });
    }

    assignPersonToSpace(person, space) {
        // Visual assignment - add person name to space
        const existingText = space.parentNode.querySelector(`text[data-person="${person.id}"]`);
        if (existingText) {
            existingText.remove();
        }

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        const spaceX = parseFloat(space.getAttribute('x'));
        const spaceY = parseFloat(space.getAttribute('y'));
        const spaceWidth = parseFloat(space.getAttribute('width'));
        const spaceHeight = parseFloat(space.getAttribute('height'));

        text.setAttribute('x', spaceX + spaceWidth/2);
        text.setAttribute('y', spaceY + spaceHeight - 10);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '10');
        text.setAttribute('font-weight', 'bold');
        text.setAttribute('fill', '#1976d2');
        text.setAttribute('data-person', person.id);
        text.textContent = person.name;

        document.getElementById('people-layer').appendChild(text);

        // Update space data
        space.setAttribute('data-assigned-person', person.id);
        space.setAttribute('data-assigned-name', person.name);
    }

    assignPersonToSelectedSpaces(person) {
        if (this.floorPlan.selectedSpaces.length === 0) {
            this.showNotification('Please select a space first', 'warning');
            return;
        }

        // For multi-select, assign to first selected space
        const targetSpace = this.floorPlan.selectedSpaces[0];
        this.assignPersonToSpace(person, targetSpace);

        this.showNotification(`Assigned ${person.name} to space ${targetSpace.id}`, 'success');
        this.closePeopleModal();
    }

    performBulkAssignment() {
        this.showNotification('Bulk assignment feature coming soon!', 'info');
    }

    filterPeople(filterType) {
        let filteredPeople;

        switch(filterType) {
            case 'internal':
                filteredPeople = this.activePersonList.filter(p => p.type === 'internal');
                break;
            case 'contractor':
                filteredPeople = this.activePersonList.filter(p => p.type === 'contractor');
                break;
            case 'unassigned':
                filteredPeople = this.activePersonList.filter(p => !p.hasSeating);
                break;
            default:
                filteredPeople = this.activePersonList;
        }

        this.renderPeopleList(filteredPeople);
    }

    setupEquipmentDragDrop() {
        // Equipment drag and drop functionality placeholder
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 6px;
            color: white;
            font-weight: 500;
            z-index: 9999;
            opacity: 0;
            transition: opacity 0.3s;
            ${type === 'success' ? 'background: #4CAF50;' : ''}
            ${type === 'warning' ? 'background: #FF9800;' : ''}
            ${type === 'error' ? 'background: #f44336;' : ''}
            ${type === 'info' ? 'background: #2196F3;' : ''}
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => notification.style.opacity = '1', 100);
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Export for use
if (typeof window !== 'undefined') {
    window.DragDropEngine = DragDropEngine;
}