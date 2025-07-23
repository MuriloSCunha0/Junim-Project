unit uMainForm;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes,
  Vcl.Graphics, Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.Menus, Vcl.StdCtrls;

type
  TMainForm = class(TForm)
    MainMenu1: TMainMenu;
    mnuCadastros: TMenuItem;
    mnuClientes: TMenuItem;
    mnuProdutos: TMenuItem;
    mnuVendas: TMenuItem;
    mnuRelatorios: TMenuItem;
    mnuSair: TMenuItem;
    Label1: TLabel;
    procedure mnuClientesClick(Sender: TObject);
    procedure mnuProdutosClick(Sender: TObject);
    procedure mnuSairClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  MainForm: TMainForm;

implementation

uses uClientForm, uProductForm, uDataModule;

{$R *.dfm}

procedure TMainForm.FormCreate(Sender: TObject);
begin
  Caption := 'Sistema CRUD Simples - Prova de Conceito';
  Label1.Caption := 'Sistema de Gestão Simples' + #13#10 +
                   'Clientes, Produtos e Vendas' + #13#10 +
                   'Use o menu para navegar';
end;

procedure TMainForm.mnuClientesClick(Sender: TObject);
begin
  // Abrir formulário de clientes
  if not Assigned(ClientForm) then
    ClientForm := TClientForm.Create(Self);
  ClientForm.Show;
end;

procedure TMainForm.mnuProdutosClick(Sender: TObject);
begin
  // Abrir formulário de produtos
  if not Assigned(ProductForm) then
    ProductForm := TProductForm.Create(Self);
  ProductForm.Show;
end;

procedure TMainForm.mnuSairClick(Sender: TObject);
begin
  Close;
end;

end.
