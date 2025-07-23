unit uProductForm;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes,
  Vcl.Graphics, Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Data.DB, Vcl.Grids,
  Vcl.DBGrids, Vcl.DBCtrls, Vcl.StdCtrls, Vcl.ExtCtrls;

type
  TProductForm = class(TForm)
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
    Label5: TLabel;
    DBCheckBox1: TDBCheckBox;
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
  ProductForm: TProductForm;

implementation

uses uDataModule;

{$R *.dfm}

procedure TProductForm.FormCreate(Sender: TObject);
begin
  Caption := 'Cadastro de Produtos';
  DataSource1.DataSet := DataModule1.QryProdutos;
end;

procedure TProductForm.FormShow(Sender: TObject);
begin
  // Abrir query de produtos
  DataModule1.QryProdutos.SQL.Text := 'SELECT * FROM Produtos ORDER BY Nome';
  DataModule1.QryProdutos.Open;
end;

procedure TProductForm.btnNovoClick(Sender: TObject);
begin
  DataModule1.QryProdutos.Append;
  // Definir valores padrão
  DataModule1.QryProdutos.FieldByName('Ativo').AsBoolean := True;
  DataModule1.QryProdutos.FieldByName('Estoque').AsInteger := 0;
  DBEdit1.SetFocus;
end;

procedure TProductForm.btnSalvarClick(Sender: TObject);
begin
  if DataModule1.QryProdutos.State in [dsInsert, dsEdit] then
  begin
    if DBEdit1.Text = '' then
    begin
      ShowMessage('Nome do produto é obrigatório!');
      DBEdit1.SetFocus;
      Exit;
    end;
    
    if DataModule1.QryProdutos.FieldByName('Preco').AsFloat <= 0 then
    begin
      ShowMessage('Preço deve ser maior que zero!');
      DBEdit3.SetFocus;
      Exit;
    end;
    
    DataModule1.QryProdutos.Post;
    ShowMessage('Produto salvo com sucesso!');
  end;
end;

procedure TProductForm.btnCancelarClick(Sender: TObject);
begin
  DataModule1.QryProdutos.Cancel;
end;

procedure TProductForm.btnExcluirClick(Sender: TObject);
begin
  if DataModule1.QryProdutos.RecordCount > 0 then
  begin
    if MessageDlg('Confirma exclusão do produto?', mtConfirmation, [mbYes, mbNo], 0) = mrYes then
    begin
      DataModule1.QryProdutos.Delete;
      ShowMessage('Produto excluído!');
    end;
  end;
end;

end.
