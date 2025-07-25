��    f      L  �   |      �  $   �     �     �     �     	     	     	     	     	     -	     1	     5	     L	      P	  �  q	     :     W  )   s     �  �   �     &  	  =  2   G     z     �  �  �  &   l  "   �    �     �     �  z  �     ^     w     �     �     �     �     �          !     ?     E     N  �  c     =      U     v     �     �     �     �     �     �  O  �     4    M  �  g     ,     K     j  :  �  �  �     {!     �!  6  �!     �"  E  �"     B%     V%     d%     p%  p  |%     �&     �&     �&  "  '  �   &)  	    *     
*  
   *  I  "*     l+     ~+  �   �+     L,     a,     z,     �,     �,     �,     �,     -     !-  $   9-  �   ^-     ^.  �   k.     �.     /     /  �  //  .   -1     \1     {1     �1     �1     �1     �1     �1     �1     �1     �1     �1     �1  $   �1  �  2      4     4  6   94     p4  �   y4     5  I  /5  A   y6  "   �6     �6  0  �6  +   /9  1   [9  Z  �9     �;     �;  �  <     �=      �=  /   >     >>     Y>  ,   p>     �>     �>  )   �>     �>  	   ?  &   ?    2?     QA  1   pA     �A  3   �A  	   �A     �A     B     B  "   -B  �  PB     F  0  )F  R  ZG  $   �J  +   �J  '   �J  q  &K  &  �L     �N  "   �N  l  �N  %   ^P  �  �P  &   %S     LS     [S     hS  �  xS     �T     U     U  {  U  �   �W     �X     �X     �X  h  �X     BZ     _Z  �   uZ      s[     �[     �[  -   �[     �[     \     5\  1   R\     �\  &   �\    �\     �]  �   �]     �^     �^     �^     3   N   2              %           ,      0         1   
          (               L      #       F       f   >   I                   S       "   Q   `   )      '   G       ?   +   5   O   .   V      \       e   C   M          c   *      X      U   H   $   !   ]   	      K   ;   a   b   W   Z   P   @       6   D       E   /      &      T   R                         4   7   A       Y   =              <       :                   -   [   8   _   B   J         ^                        9       d                      	Available Disk Space After Cleanup: 	Available Disk Space: 	Total Disk Size: 1000mA (SW X4-Pro) 180° Mount 70% 75% 80% 800mA (SW X4-Plus) 85% 90% 900mA (recommendation) 95% Activate Manual Leveling Feature Activate Manual Leveling Feature
Klipper offers you a tool that helps adjusting the screws of your print bed. This option install the necessary configuration.

When activating this option the 'fluidd' interface will show an new "BED_SCREWS_ADJUST" button to perform the calibration. Please check guides on the web on how to use this command.

If you uncheck this option and your configuration already contains screws information, it will be left untouched. Artillery SideWinder X4 Plus Artillery SideWinder X4 Pro Artillery SideWinder X4 Unbrick Tool v0.2 Cancel Cannot find the serial port!
Please make sure that the cable is connected to the USB-C port of the printer and the printer is on. Check Model Attributes Check Model Attributes
This option checks the various model specific configurations for the selected printer model, and fixes elements that doesn't match the factory settings.

This may affect the following settings: stepper motors, printer homing, bed mesh, macros Check if Artillery Sidewinder X4 Printer Connected Complete Factory Reset Configuration Reset Configuration Reset
This option controls if your printer configuration file will be initialized to factory default.
Usually, there is no need to reset your configuration completely (leave default).

If the tool notices that your Klipper configuration is broken it will stop and suggests the reset option.
Then you have two options, with or without Klipper calibration data. If your printer behavior is absolutely weird, you should also reset calibration. Connection is not an artillery printer Detecting Serial Port of OS system Distance Sensor Offset
The offset value of the probe is slightly inconsistent on the factory settings. You can use this option to correct the offset values for the probe.

Note that Artillery mount this component on the opposite orientation of the data-sheet indication. One recommended mod is to reorient this sensor and follow the data-sheet.
If your printer has this mod, then you have to select the "180° Mount" option.

My repository contains series of tests, procedures on how to do this and also links to the data-sheet. Do not Change Do not change Enable M600
This option adds the new published macros to support the M600 filament change feature.

The following changes will be done:
	- Configuration support for beeper
	- M300 g-code (Play Tone)
	- M600 g-code (Filament Change)
	- T600 g-code (Artillery custom: Resume Print)
	
Note that if these settings are already installed the tool will not modify, neither remove them. Enabling Klipper Service Enabling Moonraker Service Enabling User Interface Service Enabling WebCam Service Erase .gcode files Erase Artillery clutter files Erase log files Erase miniature files Erase old configuration files Error Extruder Extruder Run Current Extruder Run Current
Comparing configurations of the X4-Plus and X4-Pro has an inconsistency on the extruder current, even using the same parts.
The following settings happens to exist:
	 - 800mA: SW X4-Plus
	 - 900mA: average recommendation
	 - 1000mA: SW X4=Pro

Please note that increasing the current will make your extruder stepper warmer and may cause filament softening and potential clogs. On the other side, max filament flow could benefit of it, for faster print. Factory Mount (default) Factory Reset (keep calibration) Fix file permission Fix for card resize bug G-Code Gantry General Settings Grumat Version Heatbreak Fan Speed Heatbreak Fan Speed
This option allows you to reduce the speed of the heatbreak fan. This should reduce the noise levels.

You should consider the following: the main function of this fan is to protect the filament smoothing near the entry of the hot-end, which would easily deform when the extruder pushes. As a consequence you increase the chance of causing clogs if you reduce the cooling fan.

But notice that this was designed for very high temperatures. If your max temperature never goes above 250°C you can reduce this value. This is my case and I use 90%, which already does a good job in noise levels.

Speculative Note: Artillery launched recently a new hot-end, which seems to have less heatsink mass, probably because less weight reduces vibration. On the other side, this could indicate that the old hot-end heatsink is an overkill. Higher Stepper Z Current Higher Stepper Z Current
Usually the X4-Plus model runs with 800mA stepper current for the gantry and the X4-Pro model with 900mA, which seems inconsistent, since the Plus model has more weight.

This could fix issues with Z-Axis movement, but the steppers will consume more power. Improve Mainboard Fan
On the original configuration main-board fan is only activated by the print nozzle. This configuration is OK if you are doing only printing.

But it's main function is to cool stepper motor drivers. This means that, if you activate steppers but keep the nozzle off, then perform lots of motion operations, you will overheat your stepper drivers and get errors.

By applying this option, your main-board fan will turn on as soon as any of the following elements are active: heat bed, print nozzle or any of your stepper drivers. So, I strongly recommend you set this option.

In the case you already have this modification the routine will not modify it, regardless if its 'on' or 'off'. Improved Mainboard Fan control Improved Z-Offset Error Margin Improved Z-Offset Sampling Improved Z-Offset sampling
Regardless of the orientation of your distance sensor, you can improve the Z-offset sampling by using lower approximation speeds and more samples.

By using a more accurate sampling method, the overall Z-offset errors are reduced and first layer of your prints should be more consistent. Improved Z-Offset validation
Besides improving sampling conditions you can reduce the acceptance margin of the sampled data.
This means that after performing the samples all values have to fit a lower error margin to be accepted.

Note that error margins are on the limit. If you activate this option with an unmodified printer it may happen that you printer stops with errors during Z-offset calibration and also during bed-mesh calibration. Legacy Version Limits Extruder Acceleration Limits Extruder Acceleration
Some printers have a higher extruder acceleration, that has been reduced in recent configurations, probably to avoid higher temperatures on the extruder.
This setting can help reduce extruder temperature and avoid a potential softening of your filament, and clogs as a consequence. M600: Filament Change Support Main-board Fan Speed
This option allows you to reduce the speed of the main-board fan. The main goal is to lower noise levels.

You should note that the main function of this fan is to cool down the stepper motor drivers, which may get hot depending on the intensity of acceleration and speed values. If cooling is insufficient a thermal protection of the stepper driver may occur and the motion for the affected axis stops.

In my repository I suggest the mount of a 'fan duct' that concentrates more air flow to the steppers drivers and allows you to safely reduce the fan speed. Mainboard Fan Speed Max (default) New Version Nozzle Wipe Nozzle Wipe
This macro controls how the nozzle will be cleaned and "Artillery" published two different versions of it.
The use of this g-code macro depends on your slicer software configuration.

The legacy version wipes the nozzle many times at a slower speed, but it tends to wear the wipe pad prematurely out. The new version wipes less times but at a faster speed. Offset Ok Pause Macro Pause Macro
The pause macro controls the behavior your printer when you press the pause button on the control panel.

The following options are offered:
	- Do Not Change: will not modify it
	- Legacy: Use legacy Artillery code
	- New: Use newer Artillery code
	- Grumat: My custom version.

The new version of Artillery adds support for control parameters used by the M600 command.
My custom version evaluates the filament sensor and docks the print head when filament runs out, which helps not to generate plastic purge over your printed object. Please select the correct printer.
This parameter is very critical because hardware properties of both models are very different and incompatible.

Please if you fail to set the correct option, bad things will happen! Print Bed Printer Fans Purge Line Purge Line
This macro controls how the purge line is drawn and Artillery published two different versions of it.
The use of this g-code macro depends on your slicer software configuration.

The legacy version draws lines in layers and because it causes more adhesion a newer version was developed that is very easy to be removed. Rebooting Printer Rename Fans Rename Fans
This option renames printer fans to nice names. This is used on the 'fluidd' interface.

The 'Fan 0' is renamed to 'Heatbreak Cooling Fan';
The 'Fan 2' is renamed to 'Mainboard Fan' Select Printer Model Starting Klipper Service Starting Moonraker Service Starting User Interface Service Starting WebCam Service Stopping Klipper Service Stopping Moonraker Service Stopping User Interface Service Stopping WebCam Service Temperature Reading for Host and MCU Temperature Reading for Host and MCU
If you se the 'fluidd' interface you will like this option. It activates the temperature sensors for the Host and the motion MCU.

Note that this option does not modify your settings if this sensors are already active. Temperatures There are too many compatible serial port!
Disconnect all serial port cables except for the printer that you want to apply the fix. Trimming eMMC disk Update only (default) Z-Axis Distance Sensor Project-Id-Version: unbrick-swx4
PO-Revision-Date: 2025-07-22 19:08+0200
Last-Translator: 
Language-Team: 
Language: pt_BR
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
X-Generator: Poedit 2.4.2
X-Poedit-Basepath: ../../..
Plural-Forms: nplurals=2; plural=(n != 1);
X-Poedit-KeywordsList: _;N_
X-Poedit-SourceCharset: UTF-8
X-Poedit-SearchPath-0: .
X-Poedit-SearchPathExcluded-0: assets
X-Poedit-SearchPathExcluded-1: mk-assets
X-Poedit-SearchPathExcluded-2: tests
 	Espaço em disco disponível após a limpeza: 	Espaço em disco disponível: 	Tamanho total do disco: 1000mA (SW X4-Pro) Montagem 180° 70% 75% 80% 800mA (SW X4-Plus) 85% 90% 900mA (recomendação) 95% Ativar recurso de nivelamento manual Ativar recurso de nivelamento manual
O Klipper oferece uma ferramenta que ajuda a ajustar os parafusos da sua mesa de impressão. Esta opção instala a configuração necessária.

Ao ativar esta opção, a interface 'fluidd' mostrará um novo botão "BED_SCREWS_ADJUST" para realizar a calibração. Verifique os guias na web sobre como usar este comando.

Se você desmarcar esta opção e sua configuração já contiver informações de parafusos, ela será deixada inalterada. Artillery SideWinder X4 Plus Artillery SideWinder X4 Pro Ferramenta de Desbloqueio Artillery SideWinder X4 v0.2 Cancelar Não é possível encontrar a porta serial!
Certifique-se de que o cabo esteja conectado à porta USB-C da impressora e que a impressora esteja ligada. Verificar atributos do modelo Verificar atributos do modelo
Essa opção verifica as várias configurações específicas do modelo para o modelo de impressora selecionado e corrige os elementos que não correspondem às configurações de fábrica.

Isso pode afetar as seguintes configurações: motores de passo, homing da impressora, malha de cama, macros Verifique se a impressora Artillery Sidewinder X4 está conectada Redefinição de fábrica completa Redefinição de configuração Redefinição de configuração
Esta opção controla se o arquivo de configuração da impressora será inicializado para o padrão de fábrica.
Normalmente, não há necessidade de redefinir sua configuração completamente (deixar o padrão).

Se a ferramenta perceber que sua configuração do Klipper está danificada, ela irá parar e sugerir a opção de redefinição.
Então você tem duas opções, com ou sem dados de calibração Klipper. Se o comportamento da sua impressora for absolutamente estranho, você também deve redefinir a calibração. A conexão não é uma impressora Artillery Detecção da porta serial do sistema operacional Deslocamento do sensor de distância
O valor de deslocamento da sonda é ligeiramente inconsistente nas configurações de fábrica. Você pode usar essa opção para corrigir os valores de deslocamento do teste.

Observe que a "Artillery" monta este componente na orientação oposta da indicação da folha de dados. Um mod recomendado é reorientar este sensor e seguir a folha de dados.
Se a sua impressora tiver este mod, você deverá selecionar a opção "Montagem 180°".

Meu repositório contém uma série de testes, procedimentos sobre como fazer isso e também links para a folha de dados. Não modificar Não modificar Ativar o M600
Essa opção adiciona as novas macros publicadas para dar suporte ao recurso de troca de filamento M600.

As seguintes alterações serão feitas:
	- Suporte de configuração para bipe
	- Código G M300 (Play Tone)
	- Código G M600 (Mudança de Filamento)
	- Código G T600 (personalizado de Artillery: Retomar Impressão)
	
Observe que, se essas configurações já estiverem instaladas, a ferramenta não as modificará nem as removerá. Habilitando o serviço Klipper Habilitando o serviço Moonraker Habilitando o serviço de interface do usuário Ativando o serviço WebCam Apagar arquivos .gcode Apagar arquivos desnecessários da Artillery Apagar arquivos de log Apagar arquivos de miniaturas Apagar arquivos de configuração antigos Erro Extrusora Corrente de funcionamento da extrusora Corrente de funcionamento da extrusora
A comparação das configurações do X4-Plus e do X4-Pro tem uma inconsistência na corrente da extrusora, mesmo usando as mesmas peças.
As seguintes configurações existem:
	 - 800mA: SW X4-Plus
	 - 900mA: recomendação média
	 - 1000mA: SW X4=Pro

Observe que aumentar a corrente tornará o passo da extrusora mais quente e poderá causar amolecimento do filamento e possíveis entupimentos. Por outro lado, o fluxo máximo de filamento pode se beneficiar disso, para uma impressão mais rápida. Montagem de fábrica (padrão) Redefinição de fábrica (manter a calibração) Corrigir permissão de arquivo Correção para bug de redimensionamento de cartão Código G Moldura Configurações Gerais Versão Grumat Velocidade do ventilador Heatbreak Velocidade do ventilador Heatbreak
Esta opção permite reduzir a velocidade do ventilador da garganta do hot-end. Isso deve reduzir os níveis de ruído.

Você deve considerar o seguinte: a principal função deste ventilador é proteger o alisamento do filamento perto da entrada do hot-end, que se deformaria facilmente quando a extrusora empurrasse. Como consequência, você aumenta a chance de causar entupimentos se reduzir o ventilador de resfriamento.

Mas observe que isso foi projetado para temperaturas muito altas. Se a sua temperatura máxima nunca ultrapassar 250°C, pode reduzir este valor. Este é o meu caso e uso 90%, que já faz um bom trabalho nos níveis de ruído.

Nota especulativa: A "Artillery" lançou recentemente um novo hot-end, que parece ter menos massa do dissipador de calor, provavelmente porque menos peso reduz a vibração. Por outro lado, isso pode indicar que o antigo dissipador de calor hot-end é um exagero. Corrente Z de passo mais alta Corrente Z de passo mais alta
Normalmente o modelo X4-Plus funciona com corrente de passo de 800mA para a torre e o modelo X4-Pro com 900mA, o que parece inconsistente, já que o modelo Plus tem mais peso.

Isso pode corrigir problemas com o movimento do eixo Z, mas os steppers consumirão mais energia. Melhore o ventilador da placa-mãe
Na configuração original, o ventilador da placa-mãe é ativado apenas pelo bico de impressão. Essa configuração está OK se você estiver apenas imprimindo.

Mas sua função principal é resfriar os drivers do motor de passo. Isso significa que, se você ativar os steppers, mas mantiver o bico desligado e, em seguida, executar muitas operações de movimento, você superaquecerá seus drivers de passo e obterá erros.

Ao aplicar esta opção, o ventilador da placa-mãe será ligado assim que qualquer um dos seguintes elementos estiver ativo: mesa aquecida, bico de impressão ou qualquer um dos drivers de passo. Portanto, recomendo fortemente que você defina essa opção.

Caso você já tenha essa modificação, a rotina não irá modificá-la, independentemente de estar 'ligada' ou 'desligada'. Aprimorar o ventilador da placa-mãe Margem de erro de deslocamento Z aprimorada Amostragem de deslocamento Z aprimorada Amostragem Z-Offset aprimorada
Independentemente da orientação do sensor de distância, você pode melhorar a amostragem de deslocamento Z usando velocidades de aproximação mais baixas e mais amostras.

Ao usar um método de amostragem mais preciso, os erros gerais de deslocamento Z são reduzidos e a primeira camada de suas impressões deve ser mais consistente. Validação de deslocamento Z aprimorada
Além de melhorar as condições de amostragem, você pode reduzir a margem de aceitação dos dados amostrados.
Isso significa que, após a execução das amostras, todos os valores devem se ajustar a uma margem de erro menor para serem aceitos.

Observe que as margens de erro estão no limite. Se você ativar essa opção com uma impressora não modificada, pode acontecer que a impressora pare com erros durante a calibração de deslocamento Z e também durante a calibração de malha da mesa aquecida. Versão Antiga Limita a aceleração da extrusora Limita a aceleração da extrusora
Algumas impressoras têm uma aceleração de extrusora mais alta, que foi reduzida em configurações recentes, provavelmente para evitar temperaturas mais altas na extrusora.
Esta configuração pode ajudar a reduzir a temperatura da extrusora e evitar um potencial amolecimento do filamento e, como consequência, entupimentos. M600: Suporte para troca de filamento Velocidade do ventilador da placa-mãe
Esta opção permite reduzir a velocidade do ventilador da placa-mãe. O principal objetivo é reduzir os níveis de ruído.

Você deve observar que a principal função deste ventilador é resfriar os drivers do motor de passo, que podem esquentar dependendo da intensidade dos valores de aceleração e velocidade. Se o resfriamento for insuficiente, pode ocorrer uma proteção térmica do driver de passo e o movimento do eixo afetado é interrompido.

No meu repositório, sugiro a montagem de um 'duto de ventilação' que concentra mais fluxo de ar para os drivers e permite reduzir com segurança a velocidade do ventilador. Velocidade do ventilador da placa-mãe Máx (padrão) Nova Versão Limpeza de bico Limpeza de bico
Esta macro controla como o bico será limpo e a "Artillery" publicou duas versões diferentes dele.
O uso dessa macro de código g depende da configuração do fatiador.

A versão legada limpa o bico muitas vezes em uma velocidade mais lenta, mas tende a desgastar a almofada de limpeza prematuramente. A nova versão limpa menos vezes, mas em uma velocidade mais rápida. Deslocamento Ok Macro de Pausa Pausar macro
A macro de pausa controla o comportamento da impressora quando você pressiona o botão de pausa no painel de controle.

As seguintes opções são oferecidas:
	- Não alterar: não irá modificá-lo
	- Legado: Use o código legado da Artillery
	- Novo: Use o código mais recente da Artillery
	- Grumat: Minha versão personalizada.

A nova versão da Artillery adiciona suporte para parâmetros de controle usados pelo comando M600.
Minha versão personalizada avalia o sensor de filamento e recolhe o cabeçote de impressão quando o filamento acaba, o que ajuda a não gerar purga de plástico sobre o objeto impresso. Selecione a impressora correta.
Este parâmetro é muito crítico porque as propriedades de hardware de ambos os modelos são muito diferentes e incompatíveis.

Por favor, se você não conseguir definir a opção correta, coisas ruins acontecerão! Plataforma de Construção Ventiladores de impressora Linha de purga Linha de purga
Esta macro controla como a linha de purga é desenhada e a Artillery publicou duas versões diferentes dela.
O uso dessa macro de código g depende da configuração do software fatiador.

A versão legada desenha linhas em camadas e por causar aderência demasiada, foi desenvolvida uma versão mais recente que é muito fácil de ser removida. Reinicializando a impressora Renomear Ventiladores Renomear leques
Esta opção renomeia os ventiladores da impressora para nomes bonitos. Isso é usado na interface 'fluidd'.

O 'Ventilador 0' é renomeado para 'Ventilador de resfriamento de quebra de calor';
O 'Fan 2' é renomeado para 'Mainboard Fan' Selecione o modelo da impressora Iniciando o serviço Klipper Iniciando o serviço Moonraker Iniciando o serviço de interface do usuário Iniciando o serviço WebCam Parando o serviço Klipper Parando o serviço Moonraker Interrompendo o serviço de interface do usuário Interrompendo o serviço WebCam Leitura de temperatura para host e MCU Leitura de temperatura para CPU e MCU
Se você se a interface 'fluidd', você vai gostar desta opção. Ele ativa os sensores de temperatura para a CPU e o MCU de controle de movimentos.

Observe que esta opção não modifica suas configurações se esses sensores já estiverem ativos. Temperaturas Existem muitas portas seriais compatíveis!
Desconecte todos os cabos da porta serial, exceto a impressora à qual você deseja aplicar a correção. TRIM do eMMC Atualizar apenas (padrão) Sensor de distância do eixo Z 