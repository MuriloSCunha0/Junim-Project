unit MainForm;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, DB, ADODB, Grids, DBGrids, ExtCtrls;

type
  TfrmMain = class(TForm)
    pnlTop: TPanel;
    pnlCenter: TPanel;
    btnNew: TButton;
    btnEdit: TButton;
    btnDelete: TButton;
    btnSave: TButton;
    btnCancel: TButton;
    dbgCustomers: TDBGrid;
    edtName: TEdit;
    edtEmail: TEdit;
    edtPhone: TEdit;
    lblName: TLabel;
    lblEmail: TLabel;
    lblPhone: TLabel;
    
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
    procedure btnNewClick(Sender: TObject);
    procedure btnEditClick(Sender: TObject);
    procedure btnDeleteClick(Sender: TObject);
    procedure btnSaveClick(Sender: TObject);
    procedure btnCancelClick(Sender: TObject);
    
  private
    { Private declarations }
    FCustomerID: Integer;
    procedure LoadCustomers;
    procedure ClearFields;
    procedure ValidateFields;
    function CalculateAge(BirthDate: TDateTime): Integer;
    
  public
    { Public declarations }
  end;

var
  frmMain: TfrmMain;

implementation

{$R *.dfm}

uses
  DataModule, CustomerClass, Utils;

procedure TfrmMain.FormCreate(Sender: TObject);
begin
  LoadCustomers;
  ClearFields;
end;

procedure TfrmMain.FormDestroy(Sender: TObject);
begin
  // Cleanup resources
end;

procedure TfrmMain.btnNewClick(Sender: TObject);
begin
  ClearFields;
  FCustomerID := 0;
  edtName.SetFocus;
end;

procedure TfrmMain.btnEditClick(Sender: TObject);
begin
  if dmMain.qryCustomers.RecordCount > 0 then
  begin
    FCustomerID := dmMain.qryCustomers.FieldByName('CustomerID').AsInteger;
    edtName.Text := dmMain.qryCustomers.FieldByName('Name').AsString;
    edtEmail.Text := dmMain.qryCustomers.FieldByName('Email').AsString;
    edtPhone.Text := dmMain.qryCustomers.FieldByName('Phone').AsString;
  end;
end;

procedure TfrmMain.btnDeleteClick(Sender: TObject);
begin
  if MessageDlg('Confirma exclusão?', mtConfirmation, [mbYes, mbNo], 0) = mrYes then
  begin
    try
      dmMain.DeleteCustomer(dmMain.qryCustomers.FieldByName('CustomerID').AsInteger);
      LoadCustomers;
      ShowMessage('Cliente excluído com sucesso!');
    except
      on E: Exception do
        ShowMessage('Erro ao excluir cliente: ' + E.Message);
    end;
  end;
end;

procedure TfrmMain.btnSaveClick(Sender: TObject);
var
  Customer: TCustomer;
begin
  try
    ValidateFields;
    
    Customer := TCustomer.Create;
    try
      Customer.ID := FCustomerID;
      Customer.Name := edtName.Text;
      Customer.Email := edtEmail.Text;
      Customer.Phone := edtPhone.Text;
      
      if FCustomerID = 0 then
        dmMain.InsertCustomer(Customer)
      else
        dmMain.UpdateCustomer(Customer);
        
      LoadCustomers;
      ClearFields;
      ShowMessage('Cliente salvo com sucesso!');
      
    finally
      Customer.Free;
    end;
    
  except
    on E: Exception do
      ShowMessage('Erro ao salvar cliente: ' + E.Message);
  end;
end;

procedure TfrmMain.btnCancelClick(Sender: TObject);
begin
  ClearFields;
  FCustomerID := 0;
end;

procedure TfrmMain.LoadCustomers;
begin
  try
    dmMain.qryCustomers.Close;
    dmMain.qryCustomers.Open;
  except
    on E: Exception do
      ShowMessage('Erro ao carregar clientes: ' + E.Message);
  end;
end;

procedure TfrmMain.ClearFields;
begin
  edtName.Clear;
  edtEmail.Clear;
  edtPhone.Clear;
  FCustomerID := 0;
end;

procedure TfrmMain.ValidateFields;
begin
  if Trim(edtName.Text) = '' then
    raise Exception.Create('Nome é obrigatório');
    
  if Trim(edtEmail.Text) = '' then
    raise Exception.Create('Email é obrigatório');
    
  if not IsValidEmail(edtEmail.Text) then
    raise Exception.Create('Email inválido');
end;

function TfrmMain.CalculateAge(BirthDate: TDateTime): Integer;
begin
  Result := YearsBetween(Now, BirthDate);
end;

end.
