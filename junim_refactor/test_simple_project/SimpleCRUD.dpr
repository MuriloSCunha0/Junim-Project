program SimpleCRUD;

uses
  Vcl.Forms,
  uMainForm in 'uMainForm.pas' {MainForm},
  uDataModule in 'uDataModule.pas' {DataModule1: TDataModule},
  uClientForm in 'uClientForm.pas' {ClientForm},
  uProductForm in 'uProductForm.pas' {ProductForm};

{$R *.res}

begin
  Application.Initialize;
  Application.MainFormOnTaskbar := True;
  Application.CreateForm(TDataModule1, DataModule1);
  Application.CreateForm(TMainForm, MainForm);
  Application.Run;
end.
