"""
Technique Selector — Selecciona la mejor técnica según target y objetivo.
"""
import yaml
from typing import Dict, List

TECHNIQUE_DB = {
    "initial_access": {
        "Siemens": {
            "priority": [
                {"technique": "plc_s7_password_crack", "description": "Crack S7-1200/1500 password"},
                {"technique": "plc_s7_extract", "description": "Extract program blocks"},
                {"technique": "mitm_arp_spoof", "description": "ARP spoof for credential sniffing"},
            ]
        },
        "Rockwell/Allen-Bradley": {
            "priority": [
                {"technique": "plc_cip_tag_enum", "description": "Enumerate CIP tags"},
                {"technique": "plc_cip_tag_write", "description": "Write CIP tags for control"},
            ]
        },
        "Schneider": {
            "priority": [
                {"technique": "plc_modbus_read", "description": "Read Modbus registers"},
                {"technique": "plc_modbus_write", "description": "Write Modbus registers"},
            ]
        },
        "Multiple (DNP3-capable RTU)": {
            "priority": [
                {"technique": "rtu_dnp3_recon", "description": "DNP3 Class 0 enumeration"},
                {"technique": "rtu_dnp3_crob", "description": "CROB injection"},
            ]
        },
        "Generic": {
            "priority": [
                {"technique": "plc_modbus_read", "description": "Try generic Modbus"},
            ]
        }
    },
    "persistence": {
        "Siemens": {
            "priority": [
                {"technique": "persist_plc_fw_rootkit", "description": "Firmware rootkit in PLC"},
                {"technique": "persist_wmi", "description": "WMI persistence in SCADA/EWS"},
                {"technique": "persist_multi_layer", "description": "Multi-layer deployment"},
            ]
        },
        "Generic": {
            "priority": [
                {"technique": "persist_modbus_covert", "description": "Modbus covert channel"},
                {"technique": "persist_wmi", "description": "WMI event subscription"},
            ]
        }
    },
    "c2": {
        "Generic": {
            "priority": [
                {"technique": "c2_dns_tunnel", "description": "DNS tunneling C2"},
                {"technique": "c2_modbus", "description": "Modbus native C2"},
                {"technique": "c2_icmp_tunnel", "description": "ICMP echo C2"},
                {"technique": "c2_slow_beacon", "description": "Low-and-slow beacon"},
            ]
        }
    },
    "destruction": {
        "Generic": {
            "priority": [
                {"technique": "grid_industroyer_deploy", "description": "Industroyer multi-protocol attack"},
                {"technique": "rtu_iec104_mass_trip", "description": "IEC 104 mass breaker trip"},
                {"technique": "grid_cascading_failure", "description": "Cascading failure simulation"},
            ]
        }
    }
}


class TechniqueSelector:
    def select(self, target_profile: str, goal: str) -> List[Dict]:
        profile = yaml.safe_load(target_profile) if isinstance(target_profile, str) else target_profile

        vendor = profile.get("inferred_vendor", "Generic")
        attack_surface = profile.get("attack_surface", [])

        goal_techniques = TECHNIQUE_DB.get(goal, {})
        vendor_techniques = goal_techniques.get(vendor, goal_techniques.get("Generic", []))
        generic_techniques = goal_techniques.get("Generic", [])

        all_techniques = vendor_techniques + [t for t in generic_techniques if t not in vendor_techniques]

        applicable = []
        for t in all_techniques:
            technique_name = t["technique"]
            if technique_name in attack_surface or not attack_surface:
                applicable.append(t)
            elif any(prefix in technique_name for prefix in ["c2_", "persist_", "sc_", "fw_"]):
                applicable.append(t)

        return applicable if applicable else all_techniques[:3]

    def generate_attack_chain(self, target_profile: str) -> Dict:
        profile = yaml.safe_load(target_profile) if isinstance(target_profile, str) else target_profile

        chain = {}
        for goal in ["initial_access", "persistence", "c2"]:
            chain[goal] = self.select(profile, goal)

        return chain
