from pathlib import Path
import re

p = Path('src/sound_profiles.c')
s = p.read_text()
for start, end in [
    ('static const uint8_t p_tmrbass[]', 'static const uint8_t p_kisa1[]'),
    ('static const uint8_t p_kisa2[]', 'static const uint8_t p_phsr1[]'),
    ('static const uint8_t p_phsr2[]', 'static const uint8_t p_wawa_first[]'),
    ('static const uint8_t p_tmryelp[]', 'static const uint8_t p_hilo[]'),
    ('static const uint8_t p_w1p1[]', 'static const uint8_t p_wail[]'),
]:
    a=s.index(start); b=s.index(end); s=s[:a]+s[b:]
s=re.sub(r'static const uint16_t horn2_edge_intervals\[\].*?;\n','',s)
s=s.replace('  return (id==SOUND_HORN_BANK1 || id==SOUND_HORN_BANK2) ? 1U : 0U;','  return id==SOUND_HORN_BANK1 ? 1U : 0U;')
for line in ['    case SOUND_KISA_BANK2:return 2605U;\n','    case SOUND_PHSR_BANK2:return 408U;\n','    case SOUND_YELP_BANK2:return 424U;\n','    case SOUND_WAIL1_DIRECT:return 1663U;\n']:
    s=s.replace(line,'')
s=re.sub(r'    case SOUND_BASS_BANK2:\n    case SOUND_SERVICE_TMR_YELP:\n      resolved_set\(out,&prof_tmrbass,\(uint16_t\)\(elapsed%305U\),0U\); return 1U;\n','',s)
s=s.replace('    case SOUND_KISA_BANK2:resolved_set(out,&prof_kisa2,elapsed,0U);return 1U;\n','')
s=s.replace('    case SOUND_PHSR_BANK2:resolved_set(out,&prof_phsr2,(uint16_t)(elapsed%53U),0U);return 1U;\n','')
s=re.sub(r'    case SOUND_YELP_BANK2: \{.*?\n    \}\n','',s,flags=re.S)
s=re.sub(r'    case SOUND_WAIL1_DIRECT:.*?      return 0U;\n','',s,flags=re.S)
s=re.sub(r'const uint16_t \*sound_horn2_intervals.*?\n\}\n','',s,flags=re.S)
p.write_text(s)

p=Path('src/panel_router.c'); s=p.read_text()
s=s.replace('    start_direct(rf_decoder_bank()?SOUND_PHSR_BANK2:SOUND_PHSR_BANK1);','    start_direct(SOUND_PHSR_BANK1);')
s=s.replace('    if (rf_decoder_bank()) start_direct(SOUND_YELP_BANK2); else toggle_service(SERVICE_WAIL);','    toggle_service(SERVICE_WAIL);')
s=s.replace('    if (rf_decoder_bank()) start_direct(SOUND_WAIL1_DIRECT); else toggle_service(SERVICE_YELP);','    toggle_service(SERVICE_YELP);')
s=re.sub(r'  if \(rf_decoder_take_event\(RF_CMD_WAIL2\)\) \{.*?\n  \}\n','  if (rf_decoder_take_event(RF_CMD_WAIL2)) toggle_service(SERVICE_PHSR);\n',s,flags=re.S)
s=s.replace('state_start(&horn_state,rf_decoder_bank()?SOUND_HORN_BANK2:SOUND_HORN_BANK1,0U);','state_start(&horn_state,SOUND_HORN_BANK1,0U);')
s=s.replace('state_start(&bass_state,rf_decoder_bank()?SOUND_BASS_BANK2:SOUND_BASS_BANK1,0U);','state_start(&bass_state,SOUND_BASS_BANK1,0U);')
s=re.sub(r'    if \(rf_decoder_bank\(\)\) \{.*?\n    \} else state_start\(&kisa_state,SOUND_KISA_BANK1,0U\);','    state_start(&kisa_state,SOUND_KISA_BANK1,0U);',s,flags=re.S)
s=s.replace('    case SERVICE_TMR_YELP:return SOUND_SERVICE_TMR_YELP;\n','')
s=s.replace('    case SOUND_SERVICE_TMR_YELP:return SERVICE_TMR_YELP;\n','')
s=s.replace('    if (direct_state.id==SOUND_PHSR_BANK1||direct_state.id==SOUND_PHSR_BANK2) return OWNER_PHSR;','    if (direct_state.id==SOUND_PHSR_BANK1) return OWNER_PHSR;')
s=s.replace('    if (direct_state.id==SOUND_YELP_BANK2) return OWNER_YELP;\n','')
s=s.replace('    if (direct_state.id==SOUND_WAIL1_DIRECT) return OWNER_WAIL1;\n','')
p.write_text(s)

p=Path('src/sound_profiles.h'); s=p.read_text()
for token in ['  SOUND_HORN_BANK2,\n','  SOUND_BASS_BANK2,\n','  SOUND_KISA_BANK2,\n','  SOUND_PHSR_BANK2,\n','  SOUND_YELP_BANK2,\n','  SOUND_WAIL1_DIRECT,\n','  SOUND_SERVICE_TMR_YELP,\n']:
    s=s.replace(token,'')
s=s.replace('const uint16_t *sound_horn2_intervals(uint8_t *count,uint16_t *first_delay,uint8_t *initial_high);\n','')
p.write_text(s)

p=Path('src/audio_engine.c'); s=p.read_text()
s=s.replace('  if(id==SOUND_HORN_BANK1)oc_intervals=sound_horn1_intervals(&oc_count,&first_delay,&initial_high);\n  else oc_intervals=sound_horn2_intervals(&oc_count,&first_delay,&initial_high);','  oc_intervals=sound_horn1_intervals(&oc_count,&first_delay,&initial_high);')
p.write_text(s)
Path('BANK1_ONLY.txt').write_text('BANK1-only build: BANK2-specific sound profiles and routing removed. RF decoder remains intact.\n')
