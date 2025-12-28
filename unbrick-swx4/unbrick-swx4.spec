# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
	['unbrick-swx4.pyw'],
	pathex=['.'],
	binaries=[],
	datas=[
		('assets/unbrick-swx4.ico', 'assets/'),
		('assets/artillery_X4_*.cfg', 'assets/'),
		('locale/', 'locale/'),
		],
	hiddenimports=[],
	hookspath=[],
	hooksconfig={},
	runtime_hooks=[],
	excludes=[],
	noarchive=False,
	optimize=1,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
	pyz,
	a.scripts,
	a.binaries,
	a.datas,
	[],
	name='unbrick-swx4-v1.0',
	debug=False,
	bootloader_ignore_signals=False,
	strip=False,
	upx=True,
	upx_exclude=[],
	runtime_tmpdir=None,
	console=False,
	disable_windowed_traceback=False,
	argv_emulation=False,
	target_arch=None,
	codesign_identity=None,
	entitlements_file=None,
	icon='assets/unbrick-swx4.ico',
)

coll = COLLECT(
	exe,
	a.binaries,
	a.zipfiles,
	a.datas,
	strip=False,
	upx=True,
	upx_exclude=[],
	name='unbrick-swx4',
)
