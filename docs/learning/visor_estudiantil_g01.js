(() => {
  'use strict';
  const labels = {
    block_id:'Identificador del bloque',lith_code:'Código litológico',lith_status:'Estado de litología',
    topo_status:'Posición respecto a topografía',volume_status:'Estado del volumen',
    cell_volume_m3:'Volumen de celda (m³)',rock_volume_m3:'Volumen de roca (m³)',rock_fraction:'Fracción de roca',
    cu_pct_est:'Cu estimado (%)',mo_pct_est:'Mo estimado (%)',au_gt_est:'Au estimado (g/t)',
    density_t_m3_est:'Densidad estimada (t/m³)',tonnage_t:'Tonelaje del bloque (t)',
    tonnage_reason:'Causa de ausencia de tonelaje',cu_pct_n:'Compósitos usados para Cu',
    cu_pct_holes:'Sondajes usados para Cu',cu_pct_reason:'Estado de Cu',cu_pct_sample_ids:'Muestras de Cu',
    cu_pct_distances_m:'Distancias a muestras Cu (m)',cu_pct_weights:'Pesos Cu',
    density_t_m3_n:'Muestras de densidad',density_t_m3_holes:'Sondajes para densidad',
    density_t_m3_reason:'Estado de densidad',density_t_m3_sample_ids:'Muestras de densidad',
    density_t_m3_distances_m:'Distancias a densidades (m)',cu_pct_est_r50:'Cu con radio 50 m (%)',
    cu_pct_reason_r50:'Estado de Cu a 50 m',candidate_class:'Clase candidata',
    candidate_reason:'Motivo de clasificación',reserve_classification:'Clasificación de reserva',
    allocation_rule:'Regla de asignación',scenario_A_fraction:'A: fracción asignada',
    scenario_B_fraction:'B: fracción asignada',scenario_A_allocated_t:'A: movimiento asignado (t)',
    scenario_B_allocated_t:'B: movimiento asignado (t)',scenario_A_processed_t:'A: tratamiento asignado (t)',
    scenario_B_processed_t:'B: tratamiento asignado (t)',scenario_A_remaining_t:'A: inventario restante (t)',
    scenario_B_remaining_t:'B: inventario restante (t)',scenario_A_mining_opex_usd:'A: costo de mina (USD)',
    scenario_B_mining_opex_usd:'B: costo de mina (USD)',scenario_A_processing_opex_usd:'A: costo de planta (USD)',
    scenario_B_processing_opex_usd:'B: costo de planta (USD)',scenario_A_general_opex_usd:'A: costo general (USD)',
    scenario_B_general_opex_usd:'B: costo general (USD)',scenario_A_opex_usd:'A: OPEX asignado (USD)',
    scenario_B_opex_usd:'B: OPEX asignado (USD)',scenario_A_truck_capex_share_usd:'A: CAPEX de camiones asignado (USD)',
    scenario_B_truck_capex_share_usd:'B: CAPEX de camiones asignado (USD)'
  };
  const detail = document.getElementById('block-detail');
  const values={ORE_CANDIDATE:'Mineral candidato',WASTE_CANDIDATE:'Desmonte candidato',
    UNCLASSIFIED:'Sin clasificar',NOT_ASSIGNED:'Sin clasificación profesional',
    ROCK:'Roca',AIR:'Aire',PARTIAL:'Parcial',UNASSIGNED:'Sin asignar'};
  const visible = new Set(['block_id','cu_pct_est','density_t_m3_est','rock_volume_m3',
    'tonnage_t','cu_pct_holes','mo_pct_est','au_gt_est','candidate_class',
    'scenario_A_allocated_t','scenario_A_opex_usd']);
  const friendly = new Set([...visible].map(key => labels[key]));
  const rename = () => { for(const th of detail.querySelectorAll('th')){
    if(visible.has(th.textContent))th.textContent=labels[th.textContent];
    else if(!friendly.has(th.textContent))th.closest('tr')?.remove();
  } for(const td of detail.querySelectorAll('td')){
    if(values[td.textContent])td.textContent=values[td.textContent];
  }};
  new MutationObserver(rename).observe(detail,{childList:true,subtree:true});
  rename();
  for(const option of document.querySelectorAll('#class-filter option')){
    if(values[option.textContent])option.textContent=values[option.textContent];
  }
  const run = document.getElementById('run-id');
  if(run)run.textContent='verificado de G01';
  const count = document.getElementById('drawing-count');
  const renameCount = () => {
    if(count.textContent.includes('filas en el CSV completo'))
      count.textContent=count.textContent.replace('filas en el CSV completo','bloques en el modelo completo');
  };
  if(count){new MutationObserver(renameCount).observe(count,{childList:true});renameCount();}
  const id = new URLSearchParams(location.search).get('bloque');
  if(id && /^G01-B\d{3}_\d{3}_\d{3}$/.test(id)){
    document.getElementById('block-id').value=id;
    document.getElementById('inspect').click();
  }
  window.G01_STUDENT_3D_READY=true;
})();
