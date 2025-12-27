"""
OPlus ROM Converter - Core conversion logic (Q-Flash Forge)
Handles sparse image conversion and super partition creation
Supports multiple region/NV configurations
"""
import os
import sys
import json
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable, Tuple
from pathlib import Path
import struct
import shutil

# Sparse image magic
SPARSE_HEADER_MAGIC = 0xED26FF3A

@dataclass
class PartitionInfo:
    """Partition info from super_def.json"""
    name: str
    path: Optional[str]
    size: int
    group_name: str
    is_dynamic: bool = True

@dataclass
class SuperConfig:
    """Super partition configuration"""
    block_size: int
    alignment: int
    super_size: int
    groups: List[Dict]
    partitions: List[PartitionInfo]
    nv_id: str
    nv_text: str
    config_file: str  # Original config file path

@dataclass
class RegionInfo:
    """Region/NV information for selection"""
    nv_id: str
    nv_text: str
    config_path: Path
    used_size: int
    partition_count: int

@dataclass
class RawprogramEntry:
    """Entry from rawprogram XML"""
    label: str
    filename: str
    start_sector: int
    num_sectors: int
    lun: int
    sector_size: int
    sparse: bool

def get_tools_dir() -> Path:
    """Get the tools directory (bundled or development)"""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return Path(sys._MEIPASS) / 'tools'
    else:
        # Running in development
        return Path(__file__).parent.parent / 'Tools'

def is_sparse_image(img_path: Path) -> bool:
    """Check if an image file is sparse format"""
    try:
        with open(img_path, 'rb') as f:
            magic = struct.unpack('<I', f.read(4))[0]
            return magic == SPARSE_HEADER_MAGIC
    except Exception:
        return False

def get_sparse_info(img_path: Path) -> Optional[Dict]:
    """Get sparse image header info"""
    try:
        with open(img_path, 'rb') as f:
            magic = struct.unpack('<I', f.read(4))[0]
            if magic != SPARSE_HEADER_MAGIC:
                return None
            
            major_ver = struct.unpack('<H', f.read(2))[0]
            minor_ver = struct.unpack('<H', f.read(2))[0]
            file_hdr_sz = struct.unpack('<H', f.read(2))[0]
            chunk_hdr_sz = struct.unpack('<H', f.read(2))[0]
            block_size = struct.unpack('<I', f.read(4))[0]
            total_blocks = struct.unpack('<I', f.read(4))[0]
            total_chunks = struct.unpack('<I', f.read(4))[0]
            
            return {
                'version': f'{major_ver}.{minor_ver}',
                'block_size': block_size,
                'total_blocks': total_blocks,
                'total_chunks': total_chunks,
                'raw_size': block_size * total_blocks
            }
    except Exception:
        return None

def find_all_super_defs(rom_folder: Path) -> List[RegionInfo]:
    """Find all super_def.*.json files and parse region info"""
    meta_dir = rom_folder / 'META'
    if not meta_dir.exists():
        return []
    
    regions = []
    for f in sorted(meta_dir.glob('super_def.*.json')):
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
            
            nv_id = data.get('nv_id', f.stem.split('.')[-1])
            nv_text = data.get('nv_text', 'Unknown')
            
            # Get super device info
            super_device = data.get('super_device', {})
            used_size = int(super_device.get('used_size', 0))
            
            # Count partitions with data and calculate size if not provided
            partitions_with_data = [p for p in data.get('partitions', []) if p.get('path')]
            partition_count = len(partitions_with_data)
            
            # If used_size is 0, calculate from partition sizes
            if used_size == 0:
                used_size = sum(int(p.get('size', 0)) for p in partitions_with_data)
            
            regions.append(RegionInfo(
                nv_id=nv_id,
                nv_text=nv_text,
                config_path=f,
                used_size=used_size,
                partition_count=partition_count
            ))
        except Exception:
            continue
    
    return regions

def parse_super_def(json_path: Path) -> SuperConfig:
    """Parse super_def.json configuration"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Parse block devices
    block_dev = data.get('block_devices', [{}])[0]
    
    # Parse partitions
    partitions = []
    for p in data.get('partitions', []):
        # Only include partitions with path (have actual data)
        partitions.append(PartitionInfo(
            name=p.get('name', ''),
            path=p.get('path'),
            size=int(p.get('size', 0)),
            group_name=p.get('group_name', 'default'),
            is_dynamic=p.get('is_dynamic', True)
        ))
    
    return SuperConfig(
        block_size=int(block_dev.get('block_size', 4096)),
        alignment=int(block_dev.get('alignment', 1048576)),
        super_size=int(block_dev.get('size', 0)),
        groups=data.get('groups', []),
        partitions=partitions,
        nv_id=data.get('nv_id', ''),
        nv_text=data.get('nv_text', ''),
        config_file=str(json_path)
    )

def find_super_def(rom_folder: Path) -> Optional[Path]:
    """Find first super_def.json in META folder (legacy compatibility)"""
    meta_dir = rom_folder / 'META'
    if not meta_dir.exists():
        return None
    
    # Look for super_def.*.json files
    for f in meta_dir.glob('super_def.*.json'):
        return f
    
    return None

def parse_rawprogram_xml(xml_path: Path) -> List[RawprogramEntry]:
    """Parse rawprogram XML file"""
    entries = []
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    for prog in root.findall('.//program'):
        filename = prog.get('filename', '')
        if not filename:
            continue
            
        entries.append(RawprogramEntry(
            label=prog.get('label', ''),
            filename=filename,
            start_sector=int(prog.get('start_sector', 0)),
            num_sectors=int(prog.get('num_partition_sectors', 0)),
            lun=int(prog.get('physical_partition_number', 0)),
            sector_size=int(prog.get('SECTOR_SIZE_IN_BYTES', 4096)),
            sparse=prog.get('sparse', 'false').lower() == 'true'
        ))
    
    return entries

def find_rawprogram_xmls(rom_folder: Path) -> List[Path]:
    """Find all rawprogram XML files in ROM folder"""
    images_dir = rom_folder / 'IMAGES'
    if not images_dir.exists():
        images_dir = rom_folder
    
    xmls = []
    for f in images_dir.glob('rawprogram*.xml'):
        # Skip BLANK_GPT and WIPE_PARTITIONS
        if 'BLANK_GPT' not in f.name and 'WIPE_PARTITIONS' not in f.name:
            xmls.append(f)
    
    return sorted(xmls)

def convert_sparse_to_raw(
    img_path: Path,
    output_path: Path,
    log_callback: Optional[Callable[[str], None]] = None
) -> bool:
    """Convert sparse image to raw using simg2img"""
    tools_dir = get_tools_dir()
    simg2img = tools_dir / 'simg2img.exe'
    
    if not simg2img.exists():
        if log_callback:
            log_callback(f"ERROR: simg2img.exe not found at {simg2img}")
        return False
    
    if log_callback:
        log_callback(f"Converting {img_path.name}...")
    
    try:
        result = subprocess.run(
            [str(simg2img), str(img_path), str(output_path)],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )
        
        if result.returncode == 0:
            if log_callback:
                log_callback(f"Converted: {img_path.name} -> {output_path.name}")
            return True
        else:
            if log_callback:
                log_callback(f"ERROR: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        if log_callback:
            log_callback(f"ERROR: Conversion timeout for {img_path.name}")
        return False
    except Exception as e:
        if log_callback:
            log_callback(f"ERROR: {str(e)}")
        return False

def create_super_image(
    config: SuperConfig,
    rom_folder: Path,
    output_path: Path,
    log_callback: Optional[Callable[[str], None]] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> bool:
    """Create super.img from partitions using lpmake"""
    tools_dir = get_tools_dir()
    lpmake = tools_dir / 'lpmake.exe'
    
    if not lpmake.exists():
        if log_callback:
            log_callback(f"ERROR: lpmake.exe not found at {lpmake}")
        return False
    
    # Prepare temporary raw files directory
    temp_dir = output_path.parent / '_temp_raw'
    temp_dir.mkdir(exist_ok=True)
    
    # Get partitions with actual data (have path)
    data_partitions = [p for p in config.partitions if p.path]
    total = len(data_partitions)
    
    if log_callback:
        log_callback(f"Stage 1: Converting {total} images to raw...")
        log_callback(f"Region: {config.nv_text} (NV ID: {config.nv_id})")
    
    raw_files = {}
    converted = 0
    
    for i, partition in enumerate(data_partitions):
        if progress_callback:
            progress_callback(i, total * 2)  # *2 for two stages
        
        img_path = rom_folder / partition.path
        if not img_path.exists():
            if log_callback:
                log_callback(f"WARNING: {partition.path} not found, skipping")
            continue
        
        # Check if sparse
        if is_sparse_image(img_path):
            raw_path = temp_dir / f"{partition.name}.raw"
            if convert_sparse_to_raw(img_path, raw_path, log_callback):
                raw_files[partition.name] = raw_path
                converted += 1
        else:
            # Already raw, just use it
            raw_files[partition.name] = img_path
            converted += 1
            if log_callback:
                log_callback(f"Using raw: {img_path.name}")
    
    if converted == 0:
        if log_callback:
            log_callback("ERROR: No partition images found to merge")
        return False
    
    if log_callback:
        log_callback(f"Stage 2: Creating super.img with {converted} partitions...")
    
    # Build lpmake command
    cmd = [
        str(lpmake),
        '--device-size', str(config.super_size),
        '--metadata-size', '65536',
        '--metadata-slots', '3',
        '--output', str(output_path)
    ]
    
    # Collect groups that have actual partitions with data
    used_groups = set()
    for partition in data_partitions:
        if partition.name in raw_files:
            used_groups.add(partition.group_name)
    
    # Add only groups that have partitions (skip empty groups like 'default')
    added_groups = set()
    for group in config.groups:
        group_name = group.get('name', '')
        # Skip if already added or if group has no partitions
        if group_name in added_groups or group_name not in used_groups:
            continue
        max_size = group.get('maximum_size', '0')
        cmd.extend(['--group', f"{group_name}:{max_size}"])
        added_groups.add(group_name)
        if log_callback:
            log_callback(f"Added group: {group_name} (max: {int(max_size)/(1024**3):.2f} GB)")
    
    # Add partitions
    for partition in data_partitions:
        if partition.name in raw_files:
            raw_path = raw_files[partition.name]
            file_size = raw_path.stat().st_size
            cmd.extend([
                '--partition', f"{partition.name}:readonly:{file_size}:{partition.group_name}",
                '--image', f"{partition.name}={raw_path}"
            ])
    
    if log_callback:
        log_callback(f"Running lpmake with {converted} partitions...")
    
    try:
        if progress_callback:
            progress_callback(total, total * 2)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes timeout
        )
        
        if result.returncode == 0:
            size_gb = output_path.stat().st_size / (1024**3)
            if log_callback:
                log_callback(f"Super merge completed! Size: {size_gb:.2f} GB")
                log_callback(f"Output: {output_path}")
            
            # Cleanup temp files
            if log_callback:
                log_callback("Cleaning up temporary files...")
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            if progress_callback:
                progress_callback(total * 2, total * 2)
            
            return True
        else:
            if log_callback:
                log_callback(f"ERROR: lpmake failed")
                log_callback(result.stderr[:500] if result.stderr else "Unknown error")
            return False
            
    except subprocess.TimeoutExpired:
        if log_callback:
            log_callback("ERROR: lpmake timeout (>30 min)")
        return False
    except Exception as e:
        if log_callback:
            log_callback(f"ERROR: {str(e)}")
        return False

def check_super_exists(rom_folder: Path) -> bool:
    """Check if super.img already exists"""
    images_dir = rom_folder / 'IMAGES'
    super_path = images_dir / 'super.img'
    return super_path.exists()

def get_super_path(rom_folder: Path, nv_id: Optional[str] = None) -> Path:
    """Get the expected super.img path, optionally with NV ID suffix"""
    images_dir = rom_folder / 'IMAGES'
    if nv_id:
        return images_dir / f'super.{nv_id}.img'
    return images_dir / 'super.img'

def get_region_display_name(region: RegionInfo) -> str:
    """Get a display-friendly name for a region"""
    size_gb = region.used_size / (1024**3)
    return f"{region.nv_text} ({region.nv_id}) - {size_gb:.2f} GB, {region.partition_count} partitions"
