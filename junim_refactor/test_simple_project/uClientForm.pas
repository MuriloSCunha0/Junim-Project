unit uClientForm;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes,
  Vcl.Graphics, Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Data.DB, Vcl.Grids,
  Vcl.DBGrids, Vcl.DBCtrls, Vcl.StdCtrls, Vcl.ExtCtrls;

type
  TClientForm = class(TForm)
    Panel1: TPanel;
    Panel2: TPanel;
    DBGrid1: TDBGrid;
    DBNavigator1: TDBNavigator;
    Label1: TLabel;
    DBEdit1: TDBEdit;
    Label2: TLabel;
    DBEdit2: TDBEdit;
    Label3: TLabel;
    DBEdit3: TDBEdit;
    Label4: TLabel;
    DBEdit4: TDBEdit;
    btnNovo: TButton;
    btnSalvar: TButton;
    btnCancelar: TButton;
    btnExcluir: TButton;
    DataSource1: TDataSource;
    procedure FormCreate(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure btnNovoClick(Sender: TObject);
    procedure btnSalvarClick(Sender: TObject);
    procedure btnCancelarClick(Sender: TObject);
    procedure btnExcluirClick(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  ClientForm: TClientForm;

implementation

uses uDataModule;

{$R *.dfm}

procedure TClientForm.FormCreate(Sender: TObject);
begin
  Caption := 'Cadastro de Clientes';
  DataSource1.DataSet := DataModule1.QryClientes;
end;

procedure TClientForm.FormShow(Sender: TObject);
begin
  // Abrir query de clientes
  DataModule1.QryClientes.SQL.Text := 'SELECT * FROM Clientes ORDER BY Nome';
  DataModule1.QryClientes.Open;
end;

procedure TClientForm.btnNovoClick(Sender: TObject);
begin
  DataModule1.QryClientes.Append;
  DBEdit1.SetFocus;
end;

procedure TClientForm.btnSalvarClick(Sender: TObject);
begin
  if DataModule1.QryClientes.State in [dsInsert, dsEdit] then
  begin
    if DBEdit1.Text = '' then
    begin
      ShowMessage('Nome é obrigatório!');
      DBEdit1.SetFocus;
      Exit;
    end;
    
    // Definir data de cadastro para novos registros
    if DataModule1.QryClientes.State = dsInsert then
      DataModule1.QryClientes.FieldByName('DataCadastro').AsDateTime := Now;
    
    DataModule1.QryClientes.Post;
    ShowMessage('Cliente salvo com sucesso!');
  end;
end;

procedure TClientForm.btnCancelarClick(Sender: TObject);
begin
  DataModule1.QryClientes.Cancel;
end;

procedure TClientForm.btnExcluirClick(Sender: TObject);
begin
  if DataModule1.QryClientes.RecordCount > 0 then
  begin
    if MessageDlg('Confirma exclusão do cliente?', mtConfirmation, [mbYes, mbNo], 0) = mrYes then
    begin
      DataModule1.QryClientes.Delete;
      ShowMessage('Cliente excluído!');
    end;
  end;
end;

end.
