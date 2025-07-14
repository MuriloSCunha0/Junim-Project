program CustomerManager;

uses
  Forms,
  MainForm in 'MainForm.pas' {frmMain},
  DataModule in 'DataModule.pas' {dmMain: TDataModule},
  CustomerClass in 'CustomerClass.pas',
  Utils in 'Utils.pas';

{$R *.res}

begin
  Application.Initialize;
  Application.MainFormOnTaskbar := True;
  Application.CreateForm(TfrmMain, frmMain);
  Application.CreateForm(TdmMain, dmMain);
  Application.Run;
end.
