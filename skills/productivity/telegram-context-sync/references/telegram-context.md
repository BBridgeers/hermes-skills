# Telegram Context Sync — Latest State
_Updated: 2026-04-26 04:01 AM_

## Project
**Resonate Frequency Pendant** — wearable health device that programs healing frequencies via companion app + PCB hardware

## Status
- FULL project audit completed (762 files read and analyzed)
- Dual architecture: BLE (nRF52810, firmware done) vs Zero-EMF Wired (STM32L052, firmware MISSING — BLOCKER)
- Recommendation: Ship Zero-EMF first (unique USP — zero radio emission, magnetic pogo-pin, solar, ENEPIG gold electrodes)
- User chose to start with this project — about to pick first action item

## Critical Blockers
1. STM32L052 firmware needs to be written
2. Companion app needs Web Serial API for wired mode
3. iOS doesn't support Web Serial — needs native wrapper
4. PCB Gerbers need routing verification / DRC check
5. 3D enclosure needs validation against actual dimensions

## Key Paths
- Project root: /root/Resonate_Freq_Proj
- Firmware (BLE): nrf52810/firmware/nrf52_pendant_v2.c
- Firmware (Zero-EMF): DOES NOT EXIST YET
- App: Resonate_Companion_App/app/
- Hardware spec: hardware/HARDWARE_SPEC_FINAL.md
- BOM: hardware/BOM/Resonate_Pendant_BOM.csv
- Gerbers: hardware/GerberFiles_Resonate_Pendant_v2_4_26/
- Enclosures: enclosure/cyberpunk_pendant_v4.scad (+ 3 variants)
- Research: docs/EMF_Resonate_Pendant_Research.md
- Patent: docs/Patent_Draft_Resonate_Pendant.md

## Next Actions (user to choose)
1. Write STM32L052 firmware
2. Update app for Web Serial wired mode
3. Audit Gerbers
4. Validate 3D enclosure
5. Build execution plan