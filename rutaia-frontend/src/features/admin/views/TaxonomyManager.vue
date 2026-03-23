<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-end">
      <div>
        <h2 class="text-3xl font-black text-gray-800 tracking-tighter">Taxonomía del Catálogo</h2>
        <p class="text-gray-500 text-sm">Administra la estructura jerárquica de categorías y servicios.</p>
      </div>
      <div class="flex gap-2">
        <Button label="Actualizar" icon="pi pi-refresh" class="p-button-text p-button-sm" @click="loadData" :loading="loading" />
        <Button label="Nueva Raíz" icon="pi pi-plus" class="p-button-primary bg-blue-600 border-none rounded-xl font-bold shadow-lg shadow-blue-100" @click="openDialog(null)" />
      </div>
    </div>

    <!-- Stats Summary (Optional) -->
    <div class="grid grid-cols-2 md:grid-cols-6 gap-4">
        <div v-for="root in roots" :key="root.id" class="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex flex-col items-center justify-center text-center">
            <i :class="['pi', root.icon || 'pi-tag', 'text-xl mb-2', getRootColor(root.name)]"></i>
            <span class="text-[10px] uppercase font-black text-gray-400 tracking-widest">{{ root.name }}</span>
            <span class="text-lg font-black text-gray-800">{{ getRootCount(root.id) }}</span>
        </div>
    </div>

    <!-- Tree View -->
    <div class="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
      <TreeTable 
        :value="treeNodes" 
        :loading="loading"
        class="p-treetable-sm"
        responsiveLayout="scroll"
      >
        <Column field="name" header="Categoría / Nombre" expander style="min-width: 250px">
            <template #body="{ node }">
                <div class="flex items-center gap-2">
                    <i v-if="node.data.icon" :class="['pi', node.data.icon, 'text-gray-400']"></i>
                    <span :class="['font-bold', node.children?.length ? 'text-gray-800' : 'text-gray-600 font-medium']">
                        {{ node.data.name }}
                    </span>
                    <Tag v-if="!node.data.is_active" severity="danger" value="Inactivo" class="scale-75 origin-left" />
                </div>
            </template>
        </Column>
        
        <Column field="slug" header="Slug / Identificador" class="hidden md:table-cell">
            <template #body="{ node }">
                <code class="text-[10px] bg-gray-50 px-1.5 py-0.5 rounded text-gray-400">{{ node.data.slug }}</code>
            </template>
        </Column>

        <Column header="Ítems" style="width: 80px" class="text-center">
            <template #body="{ node }">
                <span :class="['text-xs font-black', node.data.itemCount > 0 ? 'text-blue-600' : 'text-gray-300']">
                    {{ node.data.itemCount }}
                </span>
            </template>
        </Column>

        <Column header="Acciones" style="width: 150px">
            <template #body="{ node }">
                <div class="flex gap-1 justify-end">
                    <Button icon="pi pi-plus" class="p-button-text p-button-sm p-button-info" @click="openDialog(node.data, true)" title="Añadir Subcategoría" />
                    <Button icon="pi pi-pencil" class="p-button-text p-button-sm p-button-secondary" @click="openDialog(node.data)" title="Editar" />
                    <Button icon="pi pi-arrow-up-right" class="p-button-text p-button-sm p-button-warning" @click="promptMove(node.data)" title="Mover" />
                    <Button icon="pi pi-trash" class="p-button-text p-button-sm p-button-danger" @click="confirmDelete(node.data)" :disabled="node.children?.length > 0" title="Eliminar" />
                </div>
            </template>
        </Column>
      </TreeTable>
    </div>

    <!-- Edit/Create Dialog -->
    <Dialog v-model:visible="displayDialog" :header="dialogHeader" :modal="true" :style="{width: '450px'}" class="p-fluid">
        <div class="space-y-4 py-2">
            <div class="p-field">
                <label class="text-[10px] uppercase font-black text-gray-400 block mb-1">Nombre</label>
                <InputText v-model="formData.name" placeholder="Ej: Glaciares" @input="onNameChange" />
            </div>
            
            <div class="p-field">
                <label class="text-[10px] uppercase font-black text-gray-400 block mb-1">Slug (Identificador Único)</label>
                <InputText v-model="formData.slug" placeholder="naturaleza-glaciares" class="p-inputtext-sm" />
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div class="p-field">
                    <label class="text-[10px] uppercase font-black text-gray-400 block mb-1">Icono (PrimeIcons)</label>
                    <div class="p-inputgroup">
                        <span class="p-inputgroup-addon"><i :class="['pi', formData.icon || 'pi-tag']"></i></span>
                        <InputText v-model="formData.icon" placeholder="pi-tag" />
                    </div>
                </div>
                <div class="p-field">
                    <label class="text-[10px] uppercase font-black text-gray-400 block mb-1">Orden</label>
                    <InputNumber v-model="formData.sort_order" :min="0" />
                </div>
            </div>

            <div class="flex items-center gap-2 pt-2">
                <Checkbox v-model="formData.is_active" :binary="true" inputId="active" />
                <label for="active" class="text-sm font-bold text-gray-700">Categoría Activa</label>
            </div>

            <div v-if="formData.parent_name" class="bg-blue-50 p-3 rounded-xl border border-blue-100">
                <span class="text-[9px] uppercase font-black text-blue-400 block">Depende de:</span>
                <span class="text-sm font-bold text-blue-800">{{ formData.parent_name }}</span>
            </div>
        </div>
        <template #footer>
            <div class="flex justify-end gap-2 pt-4">
                <Button label="Cancelar" icon="pi pi-times" class="p-button-text p-button-secondary" @click="displayDialog = false" />
                <Button label="Guardar" icon="pi pi-check" class="p-button-primary bg-blue-600 border-none px-6" @click="saveCategory" :loading="saving" />
            </div>
        </template>
    </Dialog>

    <!-- Move Dialog -->
    <Dialog v-model:visible="displayMoveDialog" header="Mover Categoría" :modal="true" :style="{width: '400px'}">
        <div class="space-y-4 py-2">
            <p class="text-sm text-gray-600">Selecciona el nuevo padre para <strong>{{ moveTarget?.name }}</strong>:</p>
            <Dropdown 
                v-model="newParentId" 
                :options="flatCategoriesList" 
                optionLabel="name" 
                optionValue="id" 
                placeholder="Raíz del sistema" 
                class="w-full"
                showClear
                filter
            />
        </div>
        <template #footer>
            <Button label="Cancelar" icon="pi pi-times" class="p-button-text p-button-secondary" @click="displayMoveDialog = false" />
            <Button label="Mover" icon="pi pi-directions" class="p-button-warning border-none px-6" @click="executeMove" :loading="moving" />
        </template>
    </Dialog>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from '@/services/axios'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

import TreeTable from 'primevue/treetable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Checkbox from 'primevue/checkbox'
import Dialog from 'primevue/dialog'
import Dropdown from 'primevue/dropdown'
import Tag from 'primevue/tag'

const toast = useToast()
const confirm = useConfirm()

// State
const categories = ref([])
const stats = ref({})
const loading = ref(false)
const saving = ref(false)
const moving = ref(false)

const displayDialog = ref(false)
const displayMoveDialog = ref(false)
const dialogHeader = ref('')
const editMode = ref(false)
const moveTarget = ref(null)
const newParentId = ref(null)

const formData = ref({
    id: null,
    name: '',
    slug: '',
    parent_id: null,
    parent_name: '',
    icon: '',
    sort_order: 0,
    is_active: true,
    root_block: ''
})

// Computeds
const treeNodes = computed(() => {
    return buildTree(categories.value, null)
})

const roots = computed(() => {
    return categories.value.filter(c => c.parent_id === null)
})

const flatCategoriesList = computed(() => {
    // List for the Move Dropdown, filtering out the target itself and its children
    if (!moveTarget.value) return categories.value
    
    const forbidden = [moveTarget.value.id]
    const findChildren = (pid) => {
        categories.value.forEach(c => {
            if (c.parent_id === pid) {
                forbidden.push(c.id)
                findChildren(c.id)
            }
        })
    }
    findChildren(moveTarget.value.id)
    
    return categories.value.filter(c => !forbidden.includes(c.id))
})


// Methods
const loadData = async () => {
    loading.value = true
    try {
        const [catRes, statRes] = await Promise.all([
            axios.get('/admin/categories'),
            axios.get('/admin/categories/stats')
        ])
        categories.value = catRes.data
        stats.value = statRes.data
    } catch (err) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los datos' })
    } finally {
        loading.value = false
    }
}

const buildTree = (list, parentId) => {
    return list
        .filter(item => item.parent_id === parentId)
        .sort((a, b) => (a.sort_order - b.sort_order) || a.name.localeCompare(b.name))
        .map(item => ({
            key: item.id.toString(),
            data: {
                ...item,
                itemCount: stats.value[item.id] || 0
            },
            children: buildTree(list, item.id)
        }))
}

const getRootCount = (rootId) => {
    // Recursive count of items in this root and children
    let count = stats.value[rootId] || 0
    const findChildren = (pid) => {
        categories.value.forEach(c => {
            if (c.parent_id === pid) {
                count += (stats.value[c.id] || 0)
                findChildren(c.id)
            }
        })
    }
    findChildren(rootId)
    return count
}

const getRootColor = (name) => {
    switch(name) {
        case 'Naturaleza': return 'text-green-500'
        case 'Servicios': return 'text-blue-500'
        case 'Infraestructura': return 'text-orange-500'
        case 'Logística': return 'text-slate-600'
        case 'Experiencias': return 'text-purple-500'
        case 'Cultura': return 'text-red-500'
        default: return 'text-gray-400'
    }
}

const onNameChange = () => {
    if (!editMode.value) {
        formData.value.slug = formData.value.name
            .toLowerCase()
            .normalize("NFD").replace(/[\u0300-\u036f]/g, "") // Remove accents
            .replace(/[^a-z0-9]/g, '-')
            .replace(/-+/g, '-')
            .replace(/^-|-$/g, '')
    }
}

const openDialog = (nodeData, asChild = false) => {
    editMode.value = !!nodeData && !asChild
    dialogHeader.value = editMode.value ? 'Editar Categoría' : (asChild ? `Nueva Subcategoría en ${nodeData.name}` : 'Nueva Categoría Raíz')
    
    if (editMode.value) {
        formData.value = { ...nodeData }
    } else {
        formData.value = {
            id: null,
            name: '',
            slug: '',
            parent_id: asChild ? nodeData.id : null,
            parent_name: asChild ? nodeData.name : '',
            icon: '',
            sort_order: 0,
            is_active: true,
            root_block: asChild ? nodeData.root_block : ''
        }
    }
    displayDialog.value = true
}

const saveCategory = async () => {
    if (!formData.value.name || !formData.value.slug) {
        toast.add({ severity: 'warn', summary: 'Campos requeridos', detail: 'El nombre y slug son obligatorios' })
        return
    }
    saving.value = true
    try {
        if (editMode.value) {
            await axios.put(`/admin/categories/${formData.value.id}`, formData.value)
            toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Categoría guardada con éxito' })
        } else {
            await axios.post('/admin/categories', formData.value)
            toast.add({ severity: 'success', summary: 'Creado', detail: 'Nueva categoría registrada' })
        }
        displayDialog.value = false
        loadData()
    } catch (err) {
        console.error(err)
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo guardar la categoría' })
    } finally {
        saving.value = false
    }
}

const promptMove = (nodeData) => {
    moveTarget.value = nodeData
    newParentId.value = nodeData.parent_id
    displayMoveDialog.value = true
}

const executeMove = async () => {
    moving.value = true
    try {
        await axios.put(`/admin/categories/${moveTarget.value.id}/move`, null, {
            params: { parent_id: newParentId.value }
        })
        toast.add({ severity: 'success', summary: 'Movido', detail: 'Jerarquía actualizada' })
        displayMoveDialog.value = false
        loadData()
    } catch (err) {
        toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'No se pudo mover' })
    } finally {
        moving.value = false
    }
}

const confirmDelete = (nodeData) => {
    confirm.require({
        message: `¿Estás seguro de eliminar "${nodeData.name}"? Esta acción no se puede deshacer.`,
        header: 'Confirmar Eliminación',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'p-button-danger',
        accept: async () => {
            try {
                await axios.delete(`/admin/categories/${nodeData.id}`)
                toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Categoría removida' })
                loadData()
            } catch (err) {
                toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'No se pudo eliminar' })
            }
        }
    })
}

onMounted(() => {
    loadData()
})
</script>

<style scoped>
:deep(.p-treetable .p-treetable-thead > tr > th) {
  background-color: #f9fafb;
  color: #1f2937;
  border-bottom: 2px solid #f3f4f6;
  font-weight: 800;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 1rem;
}

:deep(.p-treetable .p-treetable-tbody > tr) {
    transition: all 0.2s;
}

:deep(.p-treetable .p-treetable-tbody > tr:hover) {
    background-color: #f8fafc !important;
}

:deep(.p-tag) {
    font-size: 9px;
    padding: 0.2rem 0.5rem;
}
</style>
