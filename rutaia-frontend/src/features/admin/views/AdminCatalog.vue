<template>
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-[1600px] mx-auto">
      <!-- Header -->
      <div class="bg-white rounded-2xl shadow-sm p-6 mb-6 border border-gray-100">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-black text-gray-800 flex items-center">
              <i class="pi pi-database mr-3 text-blue-600 text-2xl"></i>
              Catálogo Unificado
            </h1>
            <p class="text-gray-500 mt-1">Gestión centralizada de lugares, actividades, rutas y transporte</p>
          </div>
          <div class="flex gap-3">
             <button 
              @click="openCategoryDialog"
              class="border border-gray-200 hover:bg-gray-50 text-gray-700 font-bold px-6 py-3 rounded-xl transition-all"
            >
              <i class="pi pi-tags mr-2"></i>
              Categorías
            </button>
            <button 
              @click="openCreateDialog"
              class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-bold shadow-lg shadow-blue-200 transition-all flex items-center"
            >
              <i class="pi pi-plus-circle mr-2"></i>
              Nuevo Ítem
            </button>
          </div>
        </div>

        <!-- Advanced Filters -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <span class="p-input-icon-left w-full">
            <i class="pi pi-search" />
            <InputText v-model="filters.search" placeholder="Buscar por nombre..." class="w-full rounded-xl" @keyup.enter="loadItems" />
          </span>
          <Dropdown 
            v-model="selectedFilter" 
            :options="groupedCategories" 
            optionLabel="name" 
            optionValue="id"
            optionGroupLabel="label"
            optionGroupChildren="items"
            placeholder="Filtrar por Categoría / Tipo" 
            class="md:col-span-2 w-full rounded-xl shadow-sm"
            showClear
            filter
            @change="handleFilterChange"
          />
          <button @click="loadItems" class="bg-gray-800 text-white font-bold rounded-xl px-4 py-2 hover:bg-gray-900 transition-all">
            <i class="pi pi-sync mr-2"></i> Actualizar
          </button>
        </div>
      </div>

      <!-- Main Content: List -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <DataTable 
          :value="items" 
          :loading="loading" 
          paginator 
          :rows="20"
          responsiveLayout="scroll"
          class="p-datatable-sm"
          stripedRows
        >
          <template #empty><div class="p-8 text-center text-gray-500">No se encontraron ítems.</div></template>
          
          <Column field="id" header="ID" sortable style="width: 70px"></Column>
          
          <Column header="Nombre / Tipo" sortable field="name" style="min-width: 300px">
            <template #body="{ data }">
              <div class="flex flex-col">
                <span class="font-bold text-gray-800">{{ data.name }}</span>
                <span class="text-xs uppercase font-black tracking-wider" :class="getTypeColor(data.item_type)">
                  {{ translateType(data.item_type) }}
                </span>
              </div>
            </template>
          </Column>

          <Column field="category_name" header="Categoría" sortable>
            <template #body="{ data }">
              <span class="px-2 py-1 bg-gray-100 text-gray-600 rounded-md text-[10px] font-bold">
                {{ data.category_name || 'Sin categoría' }}
              </span>
            </template>
          </Column>

          <Column field="locality_name" header="Localidad" sortable>
            <template #body="{ data }">
              <span v-if="data.locality_name" class="flex items-center text-[10px] font-bold text-blue-700">
                <i class="pi pi-map-marker mr-1"></i> {{ data.locality_name }}
              </span>
              <span v-else class="text-[10px] text-gray-400 italic">No asignada</span>
            </template>
          </Column>

          <Column header="Raíz / Bloque" style="width: 140px">
            <template #body="{ data }">
              <div v-if="getRootName(data.category_id)" class="flex items-center">
                 <Tag :severity="getRootSeverity(getRootName(data.category_id))" :value="getRootName(data.category_id)" />
              </div>
              <span v-else class="text-[10px] text-gray-400 italic">No clasificado</span>
            </template>
          </Column>

          <Column header="Ubicación" style="width: 120px">
            <template #body="{ data }">
              <div v-if="data.lat && data.lng" class="flex items-center text-xs text-green-600 font-bold">
                <i class="pi pi-map-marker mr-1"></i> Sí
              </div>
              <div v-else class="flex items-center text-xs text-gray-400">
                <i class="pi pi-map-marker mr-1 text-gray-300"></i> No
              </div>
            </template>
          </Column>

          <Column header="Info Clave" style="width: 220px">
            <template #body="{ data }">
              <div class="text-[10px] space-y-1">
                <div v-if="data.approx_cost_clp" class="font-bold text-gray-700">
                  <i class="pi pi-dollar mr-1 text-emerald-500"></i> {{ formatMoney(data.approx_cost_clp) }}
                </div>
                <div v-if="data.estimated_duration_minutes" class="text-gray-500">
                  <i class="pi pi-clock mr-1"></i> {{ formatDuration(data.estimated_duration_minutes) }}
                </div>
                
                <!-- Specialized Meta -->
                <div v-if="data.item_type === 'route' && data.extra?.distance_km" class="text-blue-600 font-bold">
                  <i class="pi pi-map mr-1"></i> {{ data.extra.distance_km }} km ({{ data.extra.difficulty }})
                </div>
                <div v-if="data.item_type === 'lodging' && data.extra?.capacity" class="text-indigo-600 font-bold">
                  <i class="pi pi-users mr-1"></i> Cap: {{ data.extra.capacity }} pax
                </div>
              </div>
            </template>
          </Column>

          <Column header="Estado" field="is_active" style="width: 100px">
            <template #body="{ data }">
              <Tag :severity="data.is_active ? 'success' : 'danger'" :value="data.is_active ? 'Activo' : 'Inactivo'" />
            </template>
          </Column>

          <Column header="Acciones" binary style="width: 120px">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button v-if="data.item_type === 'place' && ['town', 'city'].includes(data.extra?.place_subtype)" icon="pi pi-book" class="p-button-text p-button-sm p-button-success" @click="openHyperlocalDialog(data)" title="Info Hiperlocal" />
                <Button icon="pi pi-pencil" class="p-button-text p-button-sm p-button-info" @click="editItem(data)" />
                <Button icon="pi pi-trash" class="p-button-text p-button-sm p-button-danger" @click="confirmDeleteItem(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <!-- Edit/Create Dialog -->
    <Dialog 
      v-model:visible="itemDialog" 
      :header="editMode ? 'Editar Ítem' : 'Nuevo Ítem'" 
      :modal="true" 
      class="p-fluid"
      :style="{ width: '90vw', maxWidth: '1100px' }"
    >
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 py-2 min-w-0">
        <!-- Form Side -->
        <div class="lg:col-span-7 min-w-0 space-y-5 overflow-y-auto pr-2 lg:pr-4" style="max-height: 70vh;">
          <div class="min-w-0">
            <label class="block text-sm font-bold text-gray-700 mb-1.5">Nombre del Ítem *</label>
            <InputText v-model="formData.name" placeholder="Ejem: Glaciar Grey" class="w-full rounded-xl shadow-sm" />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="min-w-0">
              <label class="block text-[10px] uppercase font-black text-gray-400 mb-1.5 tracking-widest">1. Tipo de Recurso *</label>
              <Dropdown 
                v-model="formData.item_type" 
                :options="itemTypes" 
                optionLabel="label" 
                optionValue="value" 
                placeholder="Tipo..." 
                class="w-full rounded-xl shadow-sm border-gray-200" 
              />
            </div>
            <div class="min-w-0">
              <label class="block text-[10px] uppercase font-black text-gray-400 mb-1.5 tracking-widest">2. Raíz Taxonómica *</label>
              <Dropdown 
                v-model="selectedRootId" 
                :options="rootCategories" 
                optionLabel="name" 
                optionValue="id" 
                placeholder="Raíz..." 
                class="w-full rounded-xl shadow-sm border-gray-200" 
                @change="onRootChange"
              />
            </div>
          </div>

          <div v-if="selectedRootId" class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
            <div class="min-w-0">
              <label class="block text-[10px] uppercase font-black text-gray-400 mb-1.5 tracking-widest">3. Categoría Principal *</label>
              <Dropdown 
                v-model="selectedL2Id" 
                :options="l2Categories" 
                optionLabel="name" 
                optionValue="id" 
                placeholder="Categoría..." 
                class="w-full rounded-xl shadow-sm border-gray-200 font-bold" 
                @change="onL2Change"
              />
            </div>
            <div v-if="l3Categories.length > 0" class="min-w-0">
              <label class="block text-[10px] uppercase font-black text-gray-400 mb-1.5 tracking-widest">4. Subcategoría Específica</label>
              <Dropdown 
                v-model="formData.category_id" 
                :options="l3Categories" 
                optionLabel="name" 
                optionValue="id" 
                placeholder="Subcategoría..." 
                class="w-full rounded-xl shadow-sm border-gray-200" 
                showClear
              />
            </div>
          </div>

          <div class="min-w-0">
            <label class="block text-sm font-bold text-gray-700 mb-1.5">Descripción Detallada</label>
            <Textarea v-model="formData.description" rows="4" autoResize class="w-full rounded-xl shadow-sm" placeholder="Describa el lugar o actividad..." />
          </div>

          <div class="p-4 bg-slate-50 rounded-2xl border border-slate-100 min-w-0 space-y-3">
            <label class="block text-[10px] uppercase font-black text-slate-500 tracking-widest flex items-center">
              <i class="pi pi-map-marker mr-2"></i> Ubicación Territorial
            </label>
            <div class="min-w-0">
              <label class="block text-xs font-bold text-slate-700 mb-1">Localidad Base (Opcional)</label>
              <Dropdown 
                v-model="formData.locality_id" 
                :options="localities" 
                optionLabel="name" 
                optionValue="id" 
                placeholder="Seleccionar Pueblo/Localidad..." 
                class="w-full rounded-xl shadow-sm border-gray-200" 
                filter
                showClear
              />
              <p class="text-[9px] text-slate-400 mt-1">Vincule este recurso a un centro poblado para agruparlo en servicios por destino.</p>
            </div>
          </div>


          <!-- Dynamic: Place Specifics -->
          <div v-if="formData.item_type === 'place'" class="p-4 bg-orange-50/50 rounded-2xl border border-orange-100 min-w-0 space-y-4">
            <label class="block text-[10px] uppercase font-black text-orange-900 tracking-widest flex items-center">
              <i class="pi pi-tag mr-2"></i> Propósito y Contacto
            </label>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div 
                v-for="sub in placeSubtypes" 
                :key="sub.value"
                @click="formData.extra.place_subtype = sub.value"
                :class="[
                  'p-3 rounded-xl border-2 cursor-pointer transition-all flex items-center space-x-3',
                  formData.extra?.place_subtype === sub.value ? 'border-orange-500 bg-white shadow-md' : 'border-transparent bg-white/50 hover:bg-white'
                ]"
              >
                <i :class="['pi text-xl', sub.icon, formData.extra?.place_subtype === sub.value ? 'text-orange-500' : 'text-gray-400']"></i>
                <div class="text-xs font-bold leading-tight" :class="formData.extra?.place_subtype === sub.value ? 'text-orange-900' : 'text-gray-600'">{{ sub.label }}</div>
              </div>
            </div>
            
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-orange-400 block mb-1">Dirección / Referencia</label>
                <InputText v-model="formData.extra.address" placeholder="Ej: Calle Principal 123" class="p-inputtext-sm" />
              </div>
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-orange-400 block mb-1">Teléfono</label>
                <InputText v-model="formData.extra.phone" placeholder="+56 9..." class="p-inputtext-sm" />
              </div>
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-orange-400 block mb-1">Costo Entrada</label>
                <InputNumber v-model="formData.approx_cost_clp" mode="currency" currency="CLP" locale="es-CL" class="p-inputtext-sm" />
              </div>
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-orange-400 block mb-1">Tiempo Visita</label>
                <InputNumber v-model="formData.estimated_duration_minutes" suffix=" min" class="p-inputtext-sm" />
              </div>
            </div>
          </div>

          <!-- Dynamic: Lodging Specifics -->
          <div v-if="formData.item_type === 'lodging'" class="p-4 bg-indigo-50/50 rounded-2xl border border-indigo-100 min-w-0 space-y-4">
            <label class="block text-[10px] uppercase font-black text-indigo-900 tracking-widest flex items-center">
              <i class="pi pi-home mr-2"></i> Operación del Alojamiento
            </label>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-indigo-400 block mb-1">Capacidad Max</label>
                <InputNumber v-model="formData.extra.capacity" class="p-inputtext-sm" />
              </div>
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-indigo-400 block mb-1">Check-in</label>
                <InputText v-model="formData.extra.check_in" placeholder="15:00" class="p-inputtext-sm" />
              </div>
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-indigo-400 block mb-1">Check-out</label>
                <InputText v-model="formData.extra.check_out" placeholder="11:00" class="p-inputtext-sm" />
              </div>
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-indigo-400 block mb-1">Precio Base</label>
                <InputNumber v-model="formData.approx_cost_clp" mode="currency" currency="CLP" locale="es-CL" class="p-inputtext-sm" />
              </div>
            </div>
            <div class="min-w-0">
              <label class="text-[9px] uppercase font-bold text-indigo-400 block mb-2">Comodidades / Amenities</label>
              <Chips v-model="formData.extra.amenities" placeholder="WiFi, Calefacción, Estacionamiento..." class="w-full" />
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-indigo-400 block mb-1">Contacto</label>
                <InputText v-model="formData.extra.phone" placeholder="+56 9..." class="p-inputtext-sm" />
              </div>
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-indigo-400 block mb-1">Sitio Web / Reserva</label>
                <InputText v-model="formData.extra.website" placeholder="https://..." class="p-inputtext-sm" />
              </div>
            </div>
          </div>

          <!-- Dynamic: Activity Specifics -->
          <div v-if="formData.item_type === 'activity'" class="p-4 bg-cyan-50/50 rounded-2xl border border-cyan-100 min-w-0 space-y-4">
            <label class="block text-[10px] uppercase font-black text-cyan-900 tracking-widest flex items-center">
              <i class="pi pi-bolt mr-2"></i> Detalles de la Actividad
            </label>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-cyan-400 block mb-1">Intensidad</label>
                <Dropdown v-model="formData.extra.intensity" :options="intensities" optionLabel="label" optionValue="value" class="p-inputtext-sm" />
              </div>
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-cyan-400 block mb-1">Estacionalidad</label>
                <Dropdown v-model="formData.extra.seasonality" :options="seasonalityOptions" optionLabel="label" optionValue="value" class="p-inputtext-sm" />
              </div>
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-cyan-400 block mb-1">Precio x Pax</label>
                <InputNumber v-model="formData.approx_cost_clp" mode="currency" currency="CLP" locale="es-CL" class="p-inputtext-sm" />
              </div>
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-cyan-400 block mb-1">Duración Act.</label>
                <InputNumber v-model="formData.estimated_duration_minutes" suffix=" min" class="p-inputtext-sm" />
              </div>
            </div>
            <div class="flex items-center space-x-4">
              <div class="flex items-center">
                <Checkbox v-model="formData.extra.requires_booking" :binary="true" id="check_book" />
                <label for="check_book" class="ml-2 text-xs font-bold text-cyan-800">Requiere Reserva</label>
              </div>
            </div>
            <div class="min-w-0">
              <label class="text-[9px] uppercase font-bold text-cyan-400 block mb-1">Recomendaciones / Equipo</label>
              <InputText v-model="formData.extra.requirements" placeholder="Ej: Ropa térmica, zapatos trekking" class="p-inputtext-sm w-full" />
            </div>
          </div>

          <!-- Dynamic: Route Specifics -->
          <div v-if="formData.item_type === 'route'" class="p-4 bg-emerald-50/50 rounded-2xl border border-emerald-100 min-w-0 space-y-4">
            <label class="block text-[10px] uppercase font-black text-emerald-900 tracking-widest flex items-center">
              <i class="pi pi-map mr-2"></i> Ficha de la Ruta / Sendero
            </label>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-emerald-400 block mb-1">Distancia (km)</label>
                <InputNumber v-model="formData.extra.distance_km" :minFractionDigits="1" suffix=" km" class="p-inputtext-sm" />
              </div>
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-emerald-400 block mb-1">Dificultad</label>
                <Dropdown v-model="formData.extra.difficulty" :options="difficulties" optionLabel="label" optionValue="value" class="p-inputtext-sm" />
              </div>
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-emerald-400 block mb-1">Duración Est.</label>
                <InputNumber v-model="formData.estimated_duration_minutes" suffix=" min" class="p-inputtext-sm" />
              </div>
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-emerald-400 block mb-1">Desnivel (m)</label>
                <InputNumber v-model="formData.extra.elevation_gain" suffix=" m" class="p-inputtext-sm" />
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-emerald-400 block mb-1">Lugar de Inicio</label>
                <Dropdown 
                  v-model="formData.extra.origin_place_id" 
                  :options="items.filter(i => i.item_type === 'place')" 
                  optionLabel="name" 
                  optionValue="id" 
                  filter 
                  placeholder="Seleccionar..."
                  class="p-inputtext-sm"
                />
              </div>
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-emerald-400 block mb-1">Lugar de Fin</label>
                <Dropdown 
                  v-model="formData.extra.destination_place_id" 
                  :options="items.filter(i => i.item_type === 'place')" 
                  optionLabel="name" 
                  optionValue="id" 
                  filter 
                  placeholder="Seleccionar..."
                  class="p-inputtext-sm"
                />
              </div>
            </div>
          </div>


          <!-- Dynamic: Logistic & Infrastructure Specifics -->
          <div v-if="isService || isInfrastructure" :class="['p-4 rounded-2xl border min-w-0 space-y-4 mb-5', isService ? 'bg-slate-50 border-slate-200' : 'bg-stone-50 border-stone-200']">
            <label :class="['block text-[10px] uppercase font-black tracking-widest flex items-center', isService ? 'text-slate-900' : 'text-stone-900']">
              <i :class="['pi mr-2', isService ? 'pi-wrench' : 'pi-building']"></i>
              Ficha de {{ isService ? 'Servicio' : 'Infraestructura' }}: {{ logisticGroup }}
            </label>

            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-gray-400 block mb-1">Código Técnico</label>
                <InputText v-model="formData.extra.service_code" placeholder="p.ej: hospital" class="p-inputtext-sm text-[10px]"></InputText>
              </div>
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-gray-400 block mb-1">Teléfono</label>
                <InputText v-model="formData.extra.phone" placeholder="+56..." class="p-inputtext-sm text-[10px]"></InputText>
              </div>
              <div class="min-w-0 col-span-2">
                <label class="text-[9px] uppercase font-bold text-gray-400 block mb-1">Horario Atención</label>
                <InputText v-model="formData.extra.opening_hours" placeholder="L-V 09:00 - 18:00" class="p-inputtext-sm text-[10px]"></InputText>
              </div>
            </div>

            <!-- Contextual Fields based on Group -->
            <div v-if="logisticGroup.includes('Combustible')" class="space-y-3 pt-2">
              <div class="min-w-0">
                <label class="text-[9px] uppercase font-bold text-blue-400 block mb-1">Tipos de Combustible</label>
                <Chips v-model="formData.extra.fuel_types" placeholder="95, 97, Diesel..." class="w-full text-xs"></Chips>
              </div>
              <div class="flex items-center space-x-4">
                <div class="flex items-center">
                  <Checkbox v-model="formData.extra.ev_charging" :binary="true" id="check_ev"></Checkbox>
                  <label for="check_ev" class="ml-2 text-[10px] font-bold text-gray-600">Carga Eléctrica (EV)</label>
                </div>
              </div>
            </div>

            <div v-if="logisticGroup.includes('Salud')" class="flex items-center space-x-4 pt-2">
              <div class="flex items-center">
                <Checkbox v-model="formData.extra.emergency_24h" :binary="true" id="check_24h"></Checkbox>
                <label for="check_24h" class="ml-2 text-[10px] font-bold text-gray-600">Urgencias 24h</label>
              </div>
              <div class="flex items-center">
                <Checkbox v-model="formData.extra.ambulance" :binary="true" id="check_amb"></Checkbox>
                <label for="check_amb" class="ml-2 text-[10px] font-bold text-gray-600">Ambulancia Base</label>
              </div>
            </div>

            <div v-if="logisticGroup.includes('Finanzas')" class="min-w-0 pt-2">
               <label class="text-[9px] uppercase font-bold text-gray-400 block mb-1">Límite Giro (Aprox)</label>
               <InputNumber v-model="formData.extra.withdrawal_limit" mode="currency" currency="CLP" locale="es-CL" class="p-inputtext-sm"></InputNumber>
            </div>

            <div class="pt-2">
               <label class="flex items-center space-x-3 cursor-pointer">
                  <Checkbox v-model="formData.extra.is_critical" :binary="true"></Checkbox>
                  <span class="text-[10px] font-black uppercase text-red-600 tracking-tighter">Marcar como Servicio Crítico (Emergencias)</span>
               </label>
            </div>
          </div>


          <!-- Dynamic: Transport Segments -->
          <div v-if="formData.item_type === 'transport'" class="p-4 bg-purple-50/50 rounded-2xl border border-purple-100 min-w-0">
            <div class="flex justify-between items-center mb-4">
              <label class="block text-[10px] uppercase font-black text-purple-900 tracking-widest flex items-center">
                <i class="pi pi-directions mr-2"></i>
                Tramos y Servicios
              </label>
              <Button 
                label="Agregar Tramo" 
                icon="pi pi-plus" 
                class="p-button-text p-button-sm p-button-secondary" 
                @click="addSegment" 
              />
            </div>
            
            <div v-if="formData.segments?.length" class="space-y-3">
              <div v-for="(seg, idx) in formData.segments" :key="idx" class="p-3 bg-white rounded-xl shadow-sm border border-purple-50 relative group">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                  <div class="min-w-0">
                    <label class="text-[9px] uppercase font-bold text-gray-400 block mb-1">Origen</label>
                    <Dropdown 
                      v-model="seg.origin_id" 
                      :options="items.filter(i => i.item_type === 'place')" 
                      optionLabel="name" 
                      optionValue="id" 
                      filter 
                      placeholder="Punto de inicio"
                      class="p-inputtext-sm"
                    />
                  </div>
                  <div class="min-w-0">
                    <label class="text-[9px] uppercase font-bold text-gray-400 block mb-1">Destino</label>
                    <Dropdown 
                      v-model="seg.destination_id" 
                      :options="items.filter(i => i.item_type === 'place')" 
                      optionLabel="name" 
                      optionValue="id" 
                      filter 
                      placeholder="Punto de llegada"
                      class="p-inputtext-sm"
                    />
                  </div>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div class="min-w-0">
                    <label class="text-[9px] uppercase font-bold text-gray-400 block mb-1">Precio (CLP)</label>
                    <InputNumber v-model="seg.price_clp" class="p-inputtext-sm" />
                  </div>
                  <div class="min-w-0">
                    <label class="text-[9px] uppercase font-bold text-gray-400 block mb-1">Minutos</label>
                    <InputNumber v-model="seg.duration_minutes" class="p-inputtext-sm" />
                  </div>
                  <div class="min-w-0">
                    <label class="text-[9px] uppercase font-bold text-gray-400 block mb-1">Gestión</label>
                    <Button 
                      :label="`Horarios (${(seg.schedule?.weekday?.length || 0) + (seg.schedule?.saturday?.length || 0) + (seg.schedule?.sunday_holiday?.length || 0)})`"
                      icon="pi pi-clock" 
                      class="p-button-outlined p-button-sm p-button-secondary w-full text-[10px]" 
                      @click="openScheduleDialog(idx)"
                    />
                  </div>
                  <div class="min-w-0">
                    <label class="text-[9px] uppercase font-bold text-gray-400 block mb-1">Obs. Corta</label>
                    <InputText v-model="seg.observations" placeholder="Ej: Vía Carretera" class="p-inputtext-sm w-full" />
                  </div>
                </div>
                <Button 
                  icon="pi pi-times" 
                  class="p-button-rounded p-button-danger p-button-text p-button-sm absolute -top-2 -right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-white shadow-md border" 
                  @click="removeSegment(idx)"
                />
              </div>
            </div>
            <div v-else class="text-center py-6 border-2 border-dashed border-purple-100 rounded-xl">
              <p class="text-[10px] text-purple-400 font-bold uppercase tracking-widest">No hay tramos configurados</p>
            </div>
          </div>

          <div class="bg-blue-50/50 p-5 rounded-2xl border border-blue-100 shadow-sm min-w-0">
            <h3 class="text-xs font-black text-blue-900 uppercase tracking-widest mb-4 flex items-center">
              <i class="pi pi-map-marker mr-2"></i>
              Geolocalización Operativa
            </h3>

            <!-- Geocoder Search -->
            <div class="mb-5 relative">
              <label class="text-[10px] uppercase font-bold text-blue-400 mb-1.5 block">Buscar lugar o dirección</label>
              <span class="p-input-icon-left w-full">
                <i class="pi pi-search" v-if="!searchingLoc"></i>
                <i class="pi pi-spin pi-spinner" v-else></i>
                <InputText 
                  v-model="searchQuery" 
                  placeholder="Ejem: Parque Nacional Torres del Paine o restaurante..." 
                  class="w-full rounded-xl border-blue-100"
                  @input="onSearchInput"
                />
              </span>
              
              <!-- Search Results Overlay -->
              <div v-if="searchResults.length > 0" class="absolute z-[1000] w-full bg-white border border-gray-100 rounded-xl shadow-2xl mt-1 max-h-[250px] overflow-y-auto">
                <div 
                  v-for="res in searchResults" 
                  :key="res.place_id"
                  @click="selectLocation(res)"
                  class="p-3 hover:bg-blue-50 cursor-pointer border-b border-gray-50 last:border-0 transition-colors"
                >
                  <div class="text-sm font-bold text-gray-800">{{ res.display_name.split(',')[0] }}</div>
                  <div class="text-[10px] text-gray-500 truncate">{{ res.display_name }}</div>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="min-w-0">
                <label class="text-[10px] uppercase font-bold text-gray-400 mb-1 block">Latitud</label>
                <InputNumber v-model="formData.lat" :minFractionDigits="6" :maxFractionDigits="8" class="w-full rounded-lg" />
              </div>
              <div class="min-w-0">
                <label class="text-[10px] uppercase font-bold text-gray-400 mb-1 block">Longitud</label>
                <InputNumber v-model="formData.lng" :minFractionDigits="6" :maxFractionDigits="8" class="w-full rounded-lg" />
              </div>
            </div>
            
            <div class="mt-3 flex items-center justify-between">
              <p class="text-[10px] text-blue-500 font-semibold italic flex items-center">
                <i class="pi pi-info-circle mr-1"></i>
                Haz click sobre el mapa para ajustar manualmente
              </p>
              <div v-if="formData.extra?.geo_source" class="text-[9px] px-2 py-0.5 bg-blue-100 text-blue-600 rounded-full font-black uppercase tracking-tighter">
                Fuente: {{ formData.extra.geo_source }}
              </div>
            </div>
          </div>

          <div class="pt-2 min-w-0">
            <label class="flex items-center space-x-3 cursor-pointer p-2 hover:bg-gray-50 rounded-xl transition-colors">
              <Checkbox v-model="formData.is_active" :binary="true" />
              <span class="text-sm font-bold text-gray-700">Ítem visible y activo en el sistema</span>
            </label>
          </div>
        </div>

        <!-- Map Picker Side -->
        <div class="lg:col-span-5 min-w-0 h-[350px] lg:h-[70vh] border border-gray-200 rounded-2xl overflow-hidden relative shadow-inner bg-gray-50">
          <LMap 
            ref="pickerMap"
            v-if="itemDialog"
            :zoom="12" 
            :center="mapCenter"
            @click="onMapClick"
            class="w-full h-full z-0"
            :options="{ zoomControl: true }"
          >
            <LTileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" layer-type="base" name="OpenStreetMap" />
            <LMarker v-if="formData.lat && formData.lng" :lat-lng="[formData.lat, formData.lng]" />
          </LMap>
          <div v-else class="w-full h-full flex items-center justify-center text-gray-400 italic">
            <i class="pi pi-spin pi-spinner mr-2"></i> Cargando mapa...
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-between items-center w-full">
          <span class="text-xs text-gray-400 italic font-medium">* Campos obligatorios</span>
          <div class="flex gap-2">
            <Button label="Cancelar" icon="pi pi-times" class="p-button-text p-button-secondary" @click="itemDialog = false" />
            <Button :label="editMode ? 'Actualizar' : 'Crear Ítem'" :icon="editMode ? 'pi pi-save' : 'pi pi-plus'" class="p-button-primary bg-blue-600" @click="saveItem" :loading="saving" />
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Category Management Dialog -->
    <Dialog v-model:visible="catDialog" header="Gestión de Categorías" :modal="true" :style="{ width: '500px' }">
      <div class="space-y-4">
        <div class="p-3 bg-blue-50/50 rounded-xl border border-blue-100 space-y-3">
          <label class="text-[9px] uppercase font-black text-blue-900 tracking-widest block">Añadir Nueva Categoría</label>
          <div class="space-y-2">
            <InputText v-model="newCatName" placeholder="Nombre de la categoría..." class="w-full text-xs" />
            <Dropdown 
              v-model="newCatParentId" 
              :options="categories.filter(c => !c.parent_id || categories.find(p => p.id === c.parent_id && !p.parent_id))" 
              optionLabel="name" 
              optionValue="id" 
              placeholder="Seleccionar Padre (Opcional)"
              class="w-full p-inputtext-sm text-xs"
              showClear
            />
            <Button label="Crear Categoría" icon="pi pi-plus" class="p-button-info w-full" @click="createCategory" :loading="savingCat" />
          </div>
        </div>
        <div class="max-h-[400px] overflow-y-auto border border-gray-100 rounded-lg">
          <ul class="divide-y divide-gray-50">
            <li v-for="cat in categories" :key="cat.id" class="p-3 flex justify-between items-center hover:bg-gray-50">
              <span class="font-medium text-gray-700">{{ cat.name }}</span>
              <Button icon="pi pi-trash" class="p-button-text p-button-sm p-button-danger" @click="deleteCategory(cat.id)" />
            </li>
          </ul>
        </div>
      </div>
    </Dialog>

    <!-- Transport Schedule Manager Dialog -->
    <Dialog v-model:visible="scheduleDialog" header="Gestión de Horarios por Tramo" :modal="true" :style="{ width: '600px' }">
      <div class="space-y-6 py-2">
        <p class="text-xs text-gray-500 mb-4 bg-gray-50 p-3 rounded-lg border border-gray-100 italic">
          Ingresa los horarios uno a uno presionando <strong>ENTER</strong> después de cada uno. Ejemplo: 08:30, 09:40...
        </p>
        
        <div class="space-y-5">
            <div>
                <label class="block text-sm font-bold text-gray-700 mb-2 flex items-center">
                    <i class="pi pi-calendar mr-2 text-blue-500"></i> Lunes a Viernes
                </label>
                <Chips v-model="tempSchedule.weekday" separator="," placeholder="Ej: 07:30, 08:30" class="w-full" />
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-bold text-gray-700 mb-2 flex items-center">
                        <i class="pi pi-calendar-plus mr-2 text-purple-500"></i> Sábados
                    </label>
                    <Chips v-model="tempSchedule.saturday" separator="," placeholder="Ej: 09:00" class="w-full" />
                </div>
                <div>
                    <label class="block text-sm font-bold text-gray-700 mb-2 flex items-center">
                        <i class="pi pi-calendar-minus mr-2 text-orange-500"></i> Domingos / Festivos
                    </label>
                    <Chips v-model="tempSchedule.sunday_holiday" separator="," placeholder="Ej: 10:30" class="w-full" />
                </div>
            </div>
        </div>
      </div>
      <template #footer>
          <div class="flex justify-between items-center w-full">
              <span class="text-xs text-gray-400">Total: {{ tempSchedule.weekday.length + tempSchedule.saturday.length + tempSchedule.sunday_holiday.length }} horarios</span>
              <div class="flex gap-2">
                  <Button label="Cerrar" class="p-button-text p-button-secondary" @click="scheduleDialog = false" />
                  <Button label="Guardar Horarios" icon="pi pi-check" class="p-button-primary bg-blue-600" @click="saveSchedule" />
              </div>
          </div>
      </template>
    </Dialog>

    <!-- Hyperlocal Data Dialog (Territorial Context) -->
    <Dialog v-model:visible="hyperlocalDialog" :header="'Info Hiperlocal: ' + currentHyperlocalItem?.name" :modal="true" :style="{ width: '600px' }">
      <div class="space-y-4 py-2">
        <div class="min-w-0">
          <label class="block text-sm font-bold text-gray-700 mb-1.5">Descripción Cultural / Contexto</label>
          <Textarea v-model="hyperlocalData.description_cultural" rows="4" autoResize class="w-full rounded-xl shadow-sm" placeholder="Historia del pueblo, particularidades..." />
        </div>
        <div class="min-w-0 mt-4">
          <label class="block text-sm font-bold text-gray-700 mb-1.5 flex items-center">
            <i class="pi pi-list mr-2 text-blue-500"></i> Reglas Locales / Tips
          </label>
          <Chips v-model="hyperlocalData.local_rules" separator="," placeholder="Ej: El agua es potable, Comercios cierran 13 a 15h" class="w-full" />
          <p class="text-[10px] text-gray-500 mt-1">Presiona ENTER después de cada regla.</p>
        </div>
        
        <div class="min-w-0 mt-4 bg-red-50 p-4 rounded-xl border border-red-100">
          <label class="block text-sm font-bold text-red-800 mb-1.5 flex items-center">
            <i class="pi pi-phone mr-2"></i> Contactos de Emergencia
          </label>
          <p class="text-[10px] text-red-600 mb-3">Introduce los contactos en formato "Nombre: Número". Ej: Carabineros: 133</p>
          <Chips v-model="hyperlocalEmergencyArray" separator="," placeholder="Ej: Posta: +56912345678" class="w-full" />
        </div>

        <!-- Contexto Logístico Detectado (Derivación) -->
        <div class="min-w-0 mt-6 border-t pt-4">
           <label class="block text-sm font-black text-slate-800 mb-3 flex items-center justify-between">
             <span><i class="pi pi-compass mr-2 text-slate-400"></i> Contexto Logístico Detectado (10km)</span>
             <Tag v-if="nearbyServices.length" severity="info" :value="nearbyServices.length + ' servicios'"></Tag>
           </label>
           
           <div v-if="loadingNearby" class="flex justify-center py-4">
             <i class="pi pi-spin pi-spinner text-slate-300 text-xl"></i>
           </div>
           
           <div v-else-if="nearbyServices.length" class="grid grid-cols-1 gap-2 max-h-[200px] overflow-y-auto pr-2 custom-scrollbar">
             <div v-for="svc in nearbyServices" :key="svc.id" class="flex items-center justify-between p-2 bg-slate-50 border border-slate-100 rounded-lg group">
                <div class="flex items-center gap-3">
                   <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-xs shadow-sm', svc.item_type === 'transport' ? 'bg-purple-100 text-purple-600' : 'bg-white text-slate-600']">
                      <i :class="svc.item_type === 'transport' ? 'pi pi-directions' : 'pi pi-map-marker'"></i>
                   </div>
                   <div>
                      <div class="text-[11px] font-bold text-slate-700 leading-tight">{{ svc.name }}</div>
                      <div class="text-[9px] text-slate-400 flex items-center">
                        <span class="font-bold mr-2 uppercase tracking-tighter">{{ svc.category_name || 'Servicio' }}</span>
                        <span>• a {{ (svc.distance_km || 0).toFixed(1) }} km</span>
                      </div>
                   </div>
                </div>
                <!-- Mini Pill for quick status -->
                <div v-if="svc.extra?.is_critical" class="bg-red-100 text-red-600 text-[8px] font-black px-1.5 py-0.5 rounded-full uppercase tracking-tighter">Crítico</div>
             </div>
           </div>
           
           <div v-else class="text-center py-6 bg-slate-50 border border-dashed border-slate-200 rounded-xl">
              <i class="pi pi-search text-slate-300 text-xl mb-2"></i>
              <p class="text-[10px] text-slate-400">No se detectaron servicios logísticos en el radio de 10km.</p>
           </div>
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end gap-2">
          <Button label="Cancelar" class="p-button-text p-button-secondary" @click="hyperlocalDialog = false" />
          <Button label="Guardar Info" icon="pi pi-save" class="p-button-primary bg-blue-600" @click="saveHyperlocal" :loading="savingHyperlocal" />
        </div>
      </template>
    </Dialog>
    
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from '@/services/axios'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

// Leaflet
import "leaflet/dist/leaflet.css"
import { LMap, LTileLayer, LMarker } from "@vue-leaflet/vue-leaflet"

// PrimeVue Components
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'
import InputNumber from 'primevue/inputnumber'
import Checkbox from 'primevue/checkbox'
import Tag from 'primevue/tag'
import Chips from 'primevue/chips'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import Calendar from 'primevue/calendar'

const toast = useToast()
const confirm = useConfirm()

// State
const items = ref([])
const categories = ref([])
const localities = ref([])
const loading = ref(false)
const saving = ref(false)
const savingCat = ref(false)
const itemDialog = ref(false)
const catDialog = ref(false)
const editMode = ref(false)
const selectedRootId = ref(null)
const selectedL2Id = ref(null)
const newCatName = ref('')
const newCatParentId = ref(null)

// Schedule Management
const scheduleDialog = ref(false)
const activeSegmentIdx = ref(null)
const tempSchedule = ref({
  weekday: [],
  saturday: [],
  sunday_holiday: []
})

// Hyperlocal Management
const hyperlocalDialog = ref(false)
const savingHyperlocal = ref(false)
const currentHyperlocalItem = ref(null)
const hyperlocalData = ref({
  description_cultural: '',
  local_rules: []
})
const hyperlocalEmergencyArray = ref([]) // Para Chips
const nearbyServices = ref([])
const loadingNearby = ref(false)

// Geocoding
const searchQuery = ref('')
const searchResults = ref([])
const searchingLoc = ref(false)
let searchTimeout = null

const filters = ref({
  search: '',
  item_type: null,
  category_id: null
})
const selectedFilter = ref(null)
const explorerRadius = ref(10)
const explorerResults = ref([])

const loadLocalities = async () => {
  try {
    const { data } = await axios.get('/admin/localities')
    localities.value = data.sort((a,b) => a.name.localeCompare(b.name))
  } catch (err) {
    console.error('Err localities:', err)
  }
}
const loadingExplorer = ref(false)
const explorerTypeFilter = ref(null)
const explorerMap = ref(null)

const handleFilterChange = () => {
  if (!selectedFilter.value) {
    filters.value.item_type = null
    filters.value.category_id = null
  } else {
    // Buscar en los grupos
    for (const group of groupedCategories.value) {
      const found = group.items.find(i => i.id === selectedFilter.value)
      if (found) {
        // Priorizar category_id para activar el filtrado recursivo del backend
        filters.value.category_id = found.id
        filters.value.item_type = null
        break
      }
    }
  }
  loadItems()
}

const formData = ref({
  item_type: 'place',
  name: '',
  description: '',
  category_id: null,
  lat: null,
  lng: null,
  estimated_duration_minutes: null,
  approx_cost_clp: null,
  is_active: true,
  extra: {},
  segments: []
})

const placeSubtypes = [
  { label: 'Pueblo / Base', value: 'town', icon: 'pi-home' },
  { label: 'Atractivo Turístico', value: 'interest', icon: 'pi-star' },
  { label: 'Servicio de Apoyo', value: 'service', icon: 'pi-info-circle' }
]

const mapCenter = ref([-45.5752, -72.0662]) // Coyhaique / Aysén
const itemTypes = [
  { label: 'Lugar', value: 'place' },
  { label: 'Actividad', value: 'activity' },
  { label: 'Ruta', value: 'route' },
  { label: 'Transporte', value: 'transport' },
  { label: 'Alojamiento', value: 'lodging' }
]

const intensities = [
  { label: 'Baja', value: 'low', color: 'bg-green-100 text-green-700' },
  { label: 'Media', value: 'medium', color: 'bg-yellow-100 text-yellow-700' },
  { label: 'Alta', value: 'high', color: 'bg-red-100 text-red-700' }
]

const difficulties = [
  { label: 'Fácil', value: 'easy' },
  { label: 'Moderada', value: 'moderate' },
  { label: 'Difícil', value: 'hard' }
]

const seasonalityOptions = [
  { label: 'Todo el año', value: 'all_year' },
  { label: 'Solo Verano (Dic-Mar)', value: 'summer' },
  { label: 'Temporada Media/Alta', value: 'mid_high' }
]

// Mapeo inverso de nombres de raíz a item_type
const rootToType = {
  'Lugar': 'place',
  'Actividad': 'activity',
  'Hospedaje': 'lodging',
  'Alojamiento': 'lodging',
  'Transporte': 'transport',
  'Ruta': 'route',
  'Servicios': 'place',
  'Infraestructura': 'place'
}

const groupedCategories = ref([])

const rootCategories = computed(() => categories.value.filter(c => !c.parent_id))
const l2Categories = computed(() => {
  if (!selectedRootId.value) return []
  return categories.value.filter(c => c.parent_id === selectedRootId.value)
})
const l3Categories = computed(() => {
  if (!selectedL2Id.value) return []
  return categories.value.filter(c => c.parent_id === selectedL2Id.value)
})

function onRootChange() {
  selectedL2Id.value = null
  formData.value.category_id = null
}

function onL2Change() {
  // Si no hay categorías de nivel 3, el nivel 2 es el final
  if (l3Categories.value.length === 0) {
    formData.value.category_id = selectedL2Id.value
  } else {
    formData.value.category_id = null
  }
}

const selectedCategoryInfo = computed(() => {
  if (!formData.value.category_id) return null
  return categories.value.find(c => c.id === formData.value.category_id)
})

const isService = computed(() => selectedCategoryInfo.value?.rootName === 'Servicios')
const isInfrastructure = computed(() => selectedCategoryInfo.value?.rootName === 'Infraestructura')
const logisticGroup = computed(() => selectedCategoryInfo.value?.groupName || '')

const translateType = (type) => {
  const t = itemTypes.find(i => i.value === type)
  return t ? t.label : type
}

const getTypeColor = (type) => {
  switch(type) {
    case 'place': return 'text-blue-600'
    case 'activity': return 'text-blue-600'
    case 'route': return 'text-blue-600'
    case 'transport': return 'text-blue-600'
    case 'lodging': return 'text-indigo-600'
    default: return 'text-gray-600'
  }
}

const getRootName = (catId) => {
  if (!catId) return null
  for (const group of groupedCategories.value) {
    const found = group.items.find(i => i.id === catId)
    if (found) return group.label
  }
  return null
}

const getRootSeverity = (root) => {
  if (root === 'Servicios') return 'info'
  if (root === 'Infraestructura') return 'warning'
  return 'secondary'
}

const formatMoney = (val) => val ? `$${Number(val).toLocaleString('es-CL')}` : '-'
const formatDuration = (val) => {
  if (!val) return '-'
  if (val < 60) return `${val} min`
  const h = Math.floor(val / 60)
  const m = val % 60
  return m > 0 ? `${h}h ${m}m` : `${h}h`
}


// Map Logic
function onMapClick(e) {
  if (!e.latlng) return
  formData.value.lat = parseFloat(e.latlng.lat.toFixed(8))
  formData.value.lng = parseFloat(e.latlng.lng.toFixed(8))
  
  // Track source
  if (!formData.value.extra) formData.value.extra = {}
  formData.value.extra.geo_source = 'manual'
  formData.value.extra.geo_ref = null

  toast.add({ severity: 'info', summary: 'Ubicación Ajustada', detail: `Lat: ${formData.value.lat}, Lng: ${formData.value.lng}`, life: 2000 })
}

// Geocoding Logic
function onSearchInput() {
  if (searchTimeout) clearTimeout(searchTimeout)
  if (!searchQuery.value || searchQuery.value.length < 3) {
    searchResults.value = []
    return
  }
  
  searchTimeout = setTimeout(async () => {
    searchingLoc.value = true
    try {
      // Usamos Nominatim (OSM) vía fetch para evitar enviar tokens locales
      const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery.value)}&limit=5&addressdetails=1`
      const response = await fetch(url, {
        headers: {
          'Accept-Language': 'es' // Preferimos resultados en español
        }
      })
      const data = await response.json()
      searchResults.value = data
    } catch (err) {
      console.error('Geo error:', err)
    } finally {
      searchingLoc.value = false
    }
  }, 600)
}

function selectLocation(res) {
  const lat = parseFloat(res.lat)
  const lon = parseFloat(res.lon)
  
  formData.value.lat = lat
  formData.value.lng = lon
  mapCenter.value = [lat, lon]
  
  // Save metadata
  if (!formData.value.extra) formData.value.extra = {}
  formData.value.extra.geo_source = 'geocoder'
  formData.value.extra.geo_ref = res.display_name
  
  searchResults.value = []
  searchQuery.value = res.display_name.split(',')[0]
  
  toast.add({ severity: 'success', summary: 'Lugar Encontrado', detail: searchQuery.value, life: 3000 })
}

// Segment Logic
function addSegment() {
  if (!formData.value.segments) formData.value.segments = []
  formData.value.segments.push({
    origin_id: null,
    destination_id: null,
    price_clp: null,
    duration_minutes: null,
    frequency: '',
    schedule: {
      weekday: [],
      saturday: [],
      sunday_holiday: []
    },
    observations: ''
  })
}

function removeSegment(idx) {
  formData.value.segments.splice(idx, 1)
}

function openScheduleDialog(idx) {
  activeSegmentIdx.value = idx
  const seg = formData.value.segments[idx]
  
  // Clonar para no mutar directamente antes de guardar
  tempSchedule.value = {
    weekday: seg.schedule?.weekday ? [...seg.schedule.weekday] : [],
    saturday: seg.schedule?.saturday ? [...seg.schedule.saturday] : [],
    sunday_holiday: seg.schedule?.sunday_holiday ? [...seg.schedule.sunday_holiday] : []
  }
  
  scheduleDialog.value = true
}

function saveSchedule() {
  if (activeSegmentIdx.value !== null) {
    formData.value.segments[activeSegmentIdx.value].schedule = { ...tempSchedule.value }
    toast.add({ severity: 'success', summary: 'Horarios Configurados', detail: 'Los cambios se han guardado en el tramo.', life: 2000 })
  }
  scheduleDialog.value = false
}

// Hyperlocal Functions
async function openHyperlocalDialog(item) {
  currentHyperlocalItem.value = item
  hyperlocalData.value = { description_cultural: '', local_rules: [] }
  hyperlocalEmergencyArray.value = []
  
  try {
    const { data } = await axios.get(`/admin/items/${item.id}/destination-profile`)
    if (data) {
       hyperlocalData.value.description_cultural = data.description_cultural || ''
       hyperlocalData.value.local_rules = data.local_rules || []
       if (data.emergency_contacts) {
          hyperlocalEmergencyArray.value = Object.entries(data.emergency_contacts).map(([k, v]) => `${k}: ${v}`)
       }
    }
  } catch (err) {
    if (err.response?.status !== 404) {
       toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cargar la info hiperlocal' })
    }
  }
  
  loadNearbyServices(item)
  hyperlocalDialog.value = true
}

async function loadNearbyServices(item) {
  if (!item.lat || !item.lng) {
    nearbyServices.value = []
    return
  }
  loadingNearby.value = true
  try {
    const { data } = await axios.get('/admin/explorer/nearby', {
      params: { 
        lat: item.lat, 
        lng: item.lng, 
        radius_km: 10 // Radio por defecto para logística regional
      }
    })
    // Filtrar solo los que son Servicios o Infraestructura
    nearbyServices.value = data.filter(i => {
       // Necesitamos verificar si la categoría del ítem pertenece a los nuevos grupos
       // Por ahora, como no tenemos el rootName en el retorno del nearby, 
       // podemos filtrar por item_type y excluir al propio ítem
       return i.id !== item.id && (i.extra?.place_subtype === 'service' || i.item_type === 'transport')
    })
  } catch (err) {
    console.error('Err nearby:', err)
  } finally {
    loadingNearby.value = false
  }
}

async function saveHyperlocal() {
  savingHyperlocal.value = true
  try {
    const emergency_contacts = {}
    hyperlocalEmergencyArray.value.forEach(contact => {
      const parts = contact.split(':')
      if (parts.length >= 2) {
        const key = parts[0].trim()
        const val = parts.slice(1).join(':').trim()
        emergency_contacts[key] = val
      } else {
        emergency_contacts[contact.trim()] = ""
      }
    })
    
    const payload = {
      description_cultural: hyperlocalData.value.description_cultural,
      local_rules: hyperlocalData.value.local_rules,
      emergency_contacts: emergency_contacts
    }
    
    await axios.put(`/admin/items/${currentHyperlocalItem.value.id}/destination-profile`, payload)
    toast.add({ severity: 'success', summary: 'Éxito', detail: 'Información hiperlocal guardada' })
    hyperlocalDialog.value = false
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo guardar la información' })
  } finally {
    savingHyperlocal.value = false
  }
}

// Persistence
async function loadCategories() {
  try {
    const { data } = await axios.get('/admin/categories')
    
    // Resolve hierarchy for each category
    categories.value = data.map(cat => {
      const findRoot = (c) => {
        if (!c.parent_id) return c.name
        const parent = data.find(p => p.id === c.parent_id)
        return parent ? findRoot(parent) : c.name
      }

      const findGroup = (c) => {
        if (!c.parent_id) return '' // Es raíz
        const parent = data.find(p => p.id === c.parent_id)
        if (parent && !parent.parent_id) return c.name // Es L2 (el grupo)
        if (parent && parent.parent_id) return parent.name // Es L3, su padre es el grupo
        return ''
      }

      const rootName = findRoot(cat)
      const groupName = findGroup(cat)
      
      return { ...cat, rootName, groupName }
    })

    // Restaurar groupedCategories para el filtro de la tabla
    const roots = data.filter(c => c.parent_id === null)
    groupedCategories.value = roots.map(root => {
      const rootType = rootToType[root.name] || 'place'
      
      // Get all descendants recursively for the filter dropdown
      const getDescendants = (pid) => {
        let subs = data.filter(c => c.parent_id === pid)
        let results = [...subs]
        subs.forEach(s => {
          results = [...results, ...getDescendants(s.id)]
        })
        return results
      }

      const descendants = getDescendants(root.id)
      
      // Remove duplicates by ID just in case
      const uniqueItems = []
      const seen = new Set()
      
      descendants.forEach(d => {
        if (!seen.has(d.id)) {
          uniqueItems.push({ name: d.name, id: d.id, rootType })
          seen.add(d.id)
        }
      })
      
      return {
        label: root.name,
        code: rootType,
        items: [
          { name: `Todo ${root.name}`, id: root.id, rootType },
          ...uniqueItems
        ]
      }
    })

    // Also load localities
    await loadLocalities()
  } catch (err) {
    console.error('Err categories:', err)
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar las categorías' })
  }
}

// Sincronizar item_type al cambiar categoría
watch(() => formData.value.category_id, (newId) => {
  if (!newId) return
  
  const found = categories.value.find(c => c.id === newId)
  if (found) {
    const oldType = formData.value.item_type
    // Sincronizar item_type basado en la raíz
    const autoType = rootToType[found.rootName] || 'place'
    
    if (autoType && !editMode.value) {
       formData.value.item_type = autoType
       
       // Inicializar metadatos por defecto si cambió el tipo o están vacíos
       if (oldType !== autoType || !formData.value.extra) {
         if (!formData.value.extra) formData.value.extra = {}
         
         if (autoType === 'place') {
            formData.value.extra.place_subtype = (found.rootName === 'Servicios' || found.rootName === 'Infraestructura' || found.rootName === 'Logística') ? 'service' : 'interest'
            
            // Auto-generate service_code for logistics/infra
            if (found.rootName === 'Servicios' || found.rootName === 'Infraestructura' || found.rootName === 'Logística') {
              formData.value.extra.service_code = found.slug.split('-').pop()
            }
         } else if (autoType === 'lodging') {
            if (!formData.value.extra.capacity) formData.value.extra.capacity = 2
            if (!formData.value.extra.amenities) formData.value.extra.amenities = []
         } else if (autoType === 'activity') {
            if (!formData.value.extra.intensity) formData.value.extra.intensity = 'medium'
            if (formData.value.extra.requires_booking === undefined) formData.value.extra.requires_booking = false
         } else if (autoType === 'route') {
            if (!formData.value.extra.difficulty) formData.value.extra.difficulty = 'moderate'
         }
       }
    }
  }
})

async function loadItems() {
  loading.value = true
  try {
    const params = {
      search: filters.value.search || undefined,
      item_type: filters.value.item_type || undefined,
      category_id: filters.value.category_id || undefined,
      active_only: false // Admin vê todos
    }
    const { data } = await axios.get('/admin/items', { params })
    items.value = data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los ítems' })
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  editMode.value = false
  formData.value = {
    name: '',
    description: '',
    item_type: 'place',
    category_id: null,
    locality_id: null,
    lat: -45.5752,
    lng: -72.0662,
    is_active: true,
    extra: {
      place_subtype: 'interest'
    },
    segments: []
  }
  selectedRootId.value = null
  selectedL2Id.value = null
  searchQuery.value = ''
  searchResults.value = []
  itemDialog.value = true
}

function editItem(item) {
  editMode.value = true
  // Deep copy for segments and extra
  formData.value = JSON.parse(JSON.stringify(item))
  if (!formData.value.extra) formData.value.extra = {}
  if (!formData.value.segments) formData.value.segments = []
  
  searchQuery.value = ''
  searchResults.value = []

  if (item.lat && item.lng) {
    mapCenter.value = [item.lat, item.lng]
  }

  // Resolver jerarquía para los dropdowns guiados
  if (item.category_id) {
    const cat = categories.value.find(c => c.id === item.category_id)
    if (cat) {
        if (!cat.parent_id) {
            // Es raíz
            selectedRootId.value = cat.id
            selectedL2Id.value = null
        } else {
            const parent = categories.value.find(c => c.id === cat.parent_id)
            if (parent && !parent.parent_id) {
                // Es L2
                selectedRootId.value = parent.id
                selectedL2Id.value = cat.id
            } else if (parent && parent.parent_id) {
                // Es L3
                selectedRootId.value = parent.parent_id
                selectedL2Id.value = parent.id
            }
        }
    }
  }

  itemDialog.value = true
}

async function saveItem() {
  if (!formData.value.name || !formData.value.item_type) {
    toast.add({ severity: 'warn', summary: 'Incompleto', detail: 'Nombre y Tipo son obligatorios' })
    return
  }
  
  saving.value = true
  try {
    if (editMode.value) {
      await axios.put(`/admin/items/${formData.value.id}`, formData.value)
      toast.add({ severity: 'success', summary: 'Éxito', detail: 'Ítem actualizado' })
    } else {
      await axios.post('/admin/items', formData.value)
      toast.add({ severity: 'success', summary: 'Éxito', detail: 'Ítem creado' })
    }
    itemDialog.value = false
    loadItems()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo guardar el ítem' })
  } finally {
    saving.value = false
  }
}

function confirmDeleteItem(item) {
  confirm.require({
    message: `¿Seguro deseas eliminar "${item.name}"?`,
    header: 'Confirmar Eliminación',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await axios.delete(`/admin/items/${item.id}`)
        toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Ítem removido' })
        loadItems()
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar' })
      }
    }
  })
}

// Category Actions
function openCategoryDialog() {
  catDialog.value = true
}

async function createCategory() {
  if (!newCatName.value.trim()) return
  savingCat.value = true
  try {
    await axios.post('/admin/categories', { 
      name: newCatName.value,
      parent_id: newCatParentId.value
    })
    newCatName.value = ''
    newCatParentId.value = null
    loadCategories()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo crear categoría' })
  } finally {
    savingCat.value = false
  }
}

async function deleteCategory(id) {
  try {
    await axios.delete(`/admin/categories/${id}`)
    loadCategories()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Categoría en uso o error de red' })
  }
}

onMounted(() => {
  loadCategories()
  loadItems()
})
</script>

<style scoped>
:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f9fafb;
  color: #1f2937;
  border-bottom: 2px solid #f3f4f6;
  font-weight: 800;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 1rem;
}

:deep(.p-inputtext),
:deep(.p-inputnumber),
:deep(.p-inputnumber-input),
:deep(.p-dropdown),
:deep(.p-dropdown-label),
:deep(.p-select),
:deep(.p-select-label),
:deep(.p-textarea),
:deep(.p-multiselect),
:deep(.p-multiselect-label) {
  width: 100% !important;
  min-width: 0 !important;
  box-sizing: border-box !important;
}

:deep(.p-dropdown) {
  width: 100% !important;
}

:deep(.p-inputnumber) {
  display: block;
}

:deep(.p-dialog-content) {
  overflow: hidden;
}

:deep(.p-field),
:deep(.p-inputgroup),
:deep(.p-fluid .p-inputwrapper),
:deep(.grid) {
  margin-left: 0 !important;
  margin-top: 0 !important;
  margin-right: 0 !important;
}

:deep(.p-datatable .p-datatable-tbody > tr) {
  transition: all 0.2s;
}

:deep(.p-tag) {
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0.05em;
  padding: 0.25rem 0.6rem;
}
</style>
